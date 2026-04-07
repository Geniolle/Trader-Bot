from __future__ import annotations

import asyncio
import json
import logging
import os
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger(__name__)

HEARTBEAT_INTERVAL_SECONDS = 15.0
POLL_INTERVAL_SECONDS = 5.0
PROVIDER_QUOTA_COOLDOWN_SECONDS = 15 * 60
DEFAULT_INTERNAL_API_BASE_URL = "http://127.0.0.1:8000/api/v1"
DEFAULT_TWELVEDATA_BASE_URL = "https://api.twelvedata.com"


@dataclass
class SubscriptionState:
    market_type: str | None
    catalog: str | None
    symbol: str
    timeframe: str


@dataclass
class ProviderQuotaState:
    exhausted_until: datetime | None = None
    last_error_message: str | None = None

    def is_exhausted(self) -> bool:
        if self.exhausted_until is None:
            return False
        return _utc_now() < self.exhausted_until

    def remaining_seconds(self) -> int:
        if self.exhausted_until is None:
            return 0
        delta = self.exhausted_until - _utc_now()
        return max(int(delta.total_seconds()), 0)

    def mark_exhausted(self, message: str) -> None:
        self.exhausted_until = _utc_now() + timedelta(
            seconds=PROVIDER_QUOTA_COOLDOWN_SECONDS
        )
        self.last_error_message = message

    def clear(self) -> None:
        self.exhausted_until = None
        self.last_error_message = None


def _api_base_url() -> str:
    return (
        os.getenv("TRADERBOT_INTERNAL_API_BASE_URL", DEFAULT_INTERNAL_API_BASE_URL)
        .rstrip("/")
    )


def _twelvedata_base_url() -> str:
    return os.getenv("TWELVEDATA_BASE_URL", DEFAULT_TWELVEDATA_BASE_URL).rstrip("/")


def _twelvedata_api_key() -> str:
    return os.getenv("TWELVEDATA_API_KEY", "").strip()


def _safe_json_dumps(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, default=str)


async def _safe_send_json(websocket: WebSocket, payload: dict[str, Any]) -> bool:
    try:
        await websocket.send_text(_safe_json_dumps(payload))
        return True
    except WebSocketDisconnect:
        logger.info(
            "websocket_client_disconnected_during_send",
            extra={"event_payload": payload.get("event")},
        )
        return False
    except RuntimeError as exc:
        message = str(exc).lower()
        if "websocket is not connected" in message or "cannot call" in message:
            logger.info(
                "websocket_send_ignored_not_connected",
                extra={"event_payload": payload.get("event")},
            )
            return False
        logger.warning(
            "websocket_send_runtime_error",
            extra={
                "event_payload": payload.get("event"),
                "error": str(exc),
            },
        )
        return False
    except Exception as exc:
        logger.warning(
            "websocket_send_unexpected_error",
            extra={
                "event_payload": payload.get("event"),
                "error": str(exc),
            },
        )
        return False


async def _safe_receive_text(websocket: WebSocket) -> str | None:
    try:
        return await websocket.receive_text()
    except WebSocketDisconnect:
        return None
    except RuntimeError as exc:
        message = str(exc).lower()
        if "websocket is not connected" in message or "cannot call" in message:
            return None
        logger.warning("websocket_receive_runtime_error", extra={"error": str(exc)})
        return None
    except Exception as exc:
        logger.warning("websocket_receive_unexpected_error", extra={"error": str(exc)})
        return None


def _normalize_symbol(value: Any) -> str:
    return str(value or "").strip().upper()


def _normalize_timeframe(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    aliases = {
        "1min": "1m",
        "3min": "3m",
        "5min": "5m",
        "15min": "15m",
        "30min": "30m",
        "60min": "1h",
        "1hr": "1h",
        "4hr": "4h",
        "1day": "1d",
    }
    return aliases.get(normalized, normalized)


def _timeframe_to_minutes(timeframe: str) -> int:
    normalized = _normalize_timeframe(timeframe)
    if normalized == "1m":
        return 1
    if normalized == "3m":
        return 3
    if normalized == "5m":
        return 5
    if normalized == "15m":
        return 15
    if normalized == "30m":
        return 30
    if normalized == "1h":
        return 60
    if normalized == "4h":
        return 240
    if normalized == "1d":
        return 1440
    return 5


def _window_for_full_load(timeframe: str) -> timedelta:
    normalized = _normalize_timeframe(timeframe)

    if normalized in {"1m", "3m", "5m"}:
        return timedelta(days=1)
    if normalized in {"15m", "30m"}:
        return timedelta(days=3)
    if normalized in {"1h", "4h"}:
        return timedelta(days=15)
    return timedelta(days=60)


def _window_for_incremental_load(timeframe: str) -> timedelta:
    minutes = _timeframe_to_minutes(timeframe)
    bars = 50
    return timedelta(minutes=minutes * bars)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _build_range(window: timedelta) -> tuple[str, str]:
    end_at = _utc_now()
    start_at = end_at - window
    return start_at.isoformat(), end_at.isoformat()


def _provider_symbol(symbol: str) -> str:
    normalized = _normalize_symbol(symbol)

    if "/" in normalized:
        return normalized

    if len(normalized) == 6 and normalized.isalpha():
        return f"{normalized[:3]}/{normalized[3:]}"

    return normalized


def _provider_interval(timeframe: str) -> str:
    mapping = {
        "1m": "1min",
        "3m": "3min",
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "1h": "1h",
        "4h": "4h",
        "1d": "1day",
    }

    normalized = _normalize_timeframe(timeframe)
    return mapping.get(normalized, "5min")


def _parse_provider_datetime(value: str) -> datetime:
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    raise ValueError(f"Unsupported provider datetime format: {value}")


def _infer_open_time(close_time: datetime, timeframe: str) -> datetime:
    normalized = _normalize_timeframe(timeframe)

    if normalized == "1m":
        return close_time - timedelta(minutes=1)
    if normalized == "3m":
        return close_time - timedelta(minutes=3)
    if normalized == "5m":
        return close_time - timedelta(minutes=5)
    if normalized == "15m":
        return close_time - timedelta(minutes=15)
    if normalized == "30m":
        return close_time - timedelta(minutes=30)
    if normalized == "1h":
        return close_time - timedelta(hours=1)
    if normalized == "4h":
        return close_time - timedelta(hours=4)
    if normalized == "1d":
        return close_time - timedelta(days=1)

    return close_time - timedelta(minutes=5)


async def _fetch_candles_from_internal_api(
    client: httpx.AsyncClient,
    *,
    symbol: str,
    timeframe: str,
    mode: str,
) -> tuple[list[dict[str, Any]], str | None]:
    if mode == "full":
        window = _window_for_full_load(timeframe)
        limit = 5000
    else:
        window = _window_for_incremental_load(timeframe)
        limit = 1000

    start_at, end_at = _build_range(window)

    params = {
        "symbol": symbol,
        "timeframe": timeframe,
        "start_at": start_at,
        "end_at": end_at,
        "limit": str(limit),
        "mode": mode,
    }

    response = await client.get("/candles", params=params)

    if response.status_code != 200:
        return [], f"HTTP {response.status_code} ao carregar candles."

    payload = response.json()

    if isinstance(payload, list):
        items = payload
    elif isinstance(payload, dict):
        raw_items = payload.get("items")
        items = raw_items if isinstance(raw_items, list) else []
    else:
        items = []

    normalized_items: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue

        open_time = item.get("open_time")
        timeframe_value = item.get("timeframe")
        symbol_value = item.get("symbol")

        if not isinstance(open_time, str):
            continue
        if not isinstance(timeframe_value, str):
            continue
        if not isinstance(symbol_value, str):
            continue

        normalized_items.append(item)

    normalized_items.sort(key=lambda x: str(x.get("open_time") or ""))
    return normalized_items, None


def _is_quota_error(message: str) -> bool:
    normalized = message.lower()
    return (
        "run out of api credits" in normalized
        or "credits for the day" in normalized
        or "429" in normalized
        or "quota" in normalized
        or "limit being" in normalized
    )


async def _fetch_latest_candle_from_provider(
    client: httpx.AsyncClient,
    *,
    symbol: str,
    timeframe: str,
) -> tuple[dict[str, Any] | None, str | None]:
    api_key = _twelvedata_api_key()
    if not api_key:
        return None, "TWELVEDATA_API_KEY não configurada."

    provider_symbol = _provider_symbol(symbol)
    interval = _provider_interval(timeframe)

    params = {
        "symbol": provider_symbol,
        "interval": interval,
        "outputsize": "2",
        "order": "asc",
        "format": "JSON",
    }

    try:
        response = await client.get(
            f"{_twelvedata_base_url()}/time_series",
            params=params,
            headers={
                "Authorization": f"apikey {api_key}",
                "Accept": "application/json",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/136.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "close",
            },
        )
    except Exception as exc:
        return None, f"Erro ao consultar provider: {exc}"

    if response.status_code != 200:
        return None, f"Provider HTTP {response.status_code}"

    try:
        payload = response.json()
    except Exception as exc:
        return None, f"Resposta inválida do provider: {exc}"

    if payload.get("status") == "error":
        message = payload.get("message", "Erro desconhecido no provider")
        code = payload.get("code", "unknown")
        return None, f"TwelveData error ({code}): {message}"

    values = payload.get("values")
    if not isinstance(values, list) or not values:
        return None, "Provider não devolveu candles."

    latest_raw = values[-1]
    if not isinstance(latest_raw, dict):
        return None, "Último candle do provider inválido."

    provider_datetime = latest_raw.get("datetime")
    if not isinstance(provider_datetime, str) or not provider_datetime.strip():
        return None, "Provider não devolveu datetime do último candle."

    try:
        close_time = _parse_provider_datetime(provider_datetime)
    except Exception as exc:
        return None, str(exc)

    open_time = _infer_open_time(close_time, timeframe)

    candle = {
        "id": None,
        "asset_id": None,
        "symbol": _normalize_symbol(symbol),
        "timeframe": _normalize_timeframe(timeframe),
        "open_time": open_time.isoformat(),
        "close_time": close_time.isoformat(),
        "open": str(latest_raw.get("open") or "0"),
        "high": str(latest_raw.get("high") or "0"),
        "low": str(latest_raw.get("low") or "0"),
        "close": str(latest_raw.get("close") or "0"),
        "volume": str(latest_raw.get("volume") or "0"),
        "source": "twelvedata",
        "provider": "twelvedata",
        "market_session": None,
        "timezone": "UTC",
        "is_delayed": False,
        "is_mock": False,
        "count": 1,
    }

    return candle, None


def _extract_tick_payload(
    candle: dict[str, Any],
    *,
    symbol: str,
    timeframe: str,
) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "open_time": candle.get("open_time"),
        "open": candle.get("open"),
        "high": candle.get("high"),
        "low": candle.get("low"),
        "close": candle.get("close"),
        "count": candle.get("count", 1),
        "source": candle.get("source"),
        "provider": candle.get("provider"),
        "market_session": candle.get("market_session"),
        "timezone": candle.get("timezone"),
        "is_delayed": candle.get("is_delayed"),
        "is_mock": candle.get("is_mock"),
    }


def _candle_signature(candle: dict[str, Any] | None) -> str:
    if not candle:
        return ""

    parts = [
        str(candle.get("open_time") or ""),
        str(candle.get("open") or ""),
        str(candle.get("high") or ""),
        str(candle.get("low") or ""),
        str(candle.get("close") or ""),
        str(candle.get("volume") or ""),
        str(candle.get("count") or ""),
    ]
    return "|".join(parts)


async def _heartbeat_loop(
    websocket: WebSocket,
    stop_event: asyncio.Event,
) -> None:
    heartbeat_count = 0

    while not stop_event.is_set():
        try:
            await asyncio.wait_for(
                stop_event.wait(),
                timeout=HEARTBEAT_INTERVAL_SECONDS,
            )
            break
        except asyncio.TimeoutError:
            pass

        heartbeat_count += 1

        ok = await _safe_send_json(
            websocket,
            {
                "event": "heartbeat",
                "data": {
                    "count": heartbeat_count,
                    "message": "alive",
                },
            },
        )
        if not ok:
            stop_event.set()
            break


async def _subscription_stream_loop(
    websocket: WebSocket,
    stop_event: asyncio.Event,
    subscription: SubscriptionState,
) -> None:
    internal_base_url = _api_base_url()
    last_signature = ""
    last_known_candle: dict[str, Any] | None = None
    first_iteration = True
    quota_state = ProviderQuotaState()

    logger.info(
        "websocket_subscription_start",
        extra={
            "symbol": subscription.symbol,
            "timeframe": subscription.timeframe,
            "market_type": subscription.market_type,
            "catalog": subscription.catalog,
            "poll_interval_seconds": POLL_INTERVAL_SECONDS,
        },
    )

    timeout = httpx.Timeout(20.0, connect=10.0)

    async with httpx.AsyncClient(base_url=internal_base_url, timeout=timeout) as internal_client:
        async with httpx.AsyncClient(timeout=timeout) as provider_client:
            while not stop_event.is_set():
                if first_iteration:
                    candles, error_message = await _fetch_candles_from_internal_api(
                        internal_client,
                        symbol=subscription.symbol,
                        timeframe=subscription.timeframe,
                        mode="full",
                    )

                    if error_message:
                        ok = await _safe_send_json(
                            websocket,
                            {
                                "event": "provider_error",
                                "data": {
                                    "symbol": subscription.symbol,
                                    "timeframe": subscription.timeframe,
                                    "message": error_message,
                                },
                            },
                        )
                        if not ok:
                            stop_event.set()
                            break

                        await asyncio.sleep(POLL_INTERVAL_SECONDS)
                        continue

                    ok = await _safe_send_json(
                        websocket,
                        {
                            "event": "initial_candles",
                            "data": {
                                "symbol": subscription.symbol,
                                "timeframe": subscription.timeframe,
                                "candles": candles,
                            },
                        },
                    )
                    if not ok:
                        stop_event.set()
                        break

                    ok = await _safe_send_json(
                        websocket,
                        {
                            "event": "candles_refresh",
                            "data": {
                                "symbol": subscription.symbol,
                                "timeframe": subscription.timeframe,
                                "count": len(candles),
                                "reason": "initial_load",
                                "poll_seconds": POLL_INTERVAL_SECONDS,
                                "latest_open_time": (
                                    candles[-1].get("open_time") if candles else None
                                ),
                            },
                        },
                    )
                    if not ok:
                        stop_event.set()
                        break

                    if candles:
                        last_known_candle = candles[-1]
                        last_signature = _candle_signature(last_known_candle)

                    logger.info(
                        "websocket_initial_candles_sent",
                        extra={
                            "symbol": subscription.symbol,
                            "timeframe": subscription.timeframe,
                            "count": len(candles),
                            "last_signature": last_signature,
                        },
                    )

                    first_iteration = False
                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
                    continue

                if quota_state.is_exhausted():
                    latest_open_time = (
                        str(last_known_candle.get("open_time") or "")
                        if last_known_candle
                        else ""
                    )

                    logger.warning(
                        "websocket_provider_quota_cooldown_active",
                        extra={
                            "symbol": subscription.symbol,
                            "timeframe": subscription.timeframe,
                            "remaining_seconds": quota_state.remaining_seconds(),
                        },
                    )

                    ok = await _safe_send_json(
                        websocket,
                        {
                            "event": "candles_refresh",
                            "data": {
                                "symbol": subscription.symbol,
                                "timeframe": subscription.timeframe,
                                "count": 1 if last_known_candle else 0,
                                "reason": "provider_quota_exhausted",
                                "poll_seconds": POLL_INTERVAL_SECONDS,
                                "latest_open_time": latest_open_time,
                                "cooldown_seconds": quota_state.remaining_seconds(),
                            },
                        },
                    )
                    if not ok:
                        stop_event.set()
                        break

                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
                    continue

                latest_candle, provider_error = await _fetch_latest_candle_from_provider(
                    provider_client,
                    symbol=subscription.symbol,
                    timeframe=subscription.timeframe,
                )

                if provider_error:
                    logger.warning(
                        "websocket_provider_latest_failed",
                        extra={
                            "symbol": subscription.symbol,
                            "timeframe": subscription.timeframe,
                            "error": provider_error,
                        },
                    )

                    if _is_quota_error(provider_error):
                        quota_state.mark_exhausted(provider_error)

                        ok = await _safe_send_json(
                            websocket,
                            {
                                "event": "provider_error",
                                "data": {
                                    "symbol": subscription.symbol,
                                    "timeframe": subscription.timeframe,
                                    "message": provider_error,
                                },
                            },
                        )
                        if not ok:
                            stop_event.set()
                            break

                        latest_open_time = (
                            str(last_known_candle.get("open_time") or "")
                            if last_known_candle
                            else ""
                        )

                        ok = await _safe_send_json(
                            websocket,
                            {
                                "event": "candles_refresh",
                                "data": {
                                    "symbol": subscription.symbol,
                                    "timeframe": subscription.timeframe,
                                    "count": 1 if last_known_candle else 0,
                                    "reason": "provider_quota_exhausted",
                                    "poll_seconds": POLL_INTERVAL_SECONDS,
                                    "latest_open_time": latest_open_time,
                                    "cooldown_seconds": quota_state.remaining_seconds(),
                                },
                            },
                        )
                        if not ok:
                            stop_event.set()
                            break

                        await asyncio.sleep(POLL_INTERVAL_SECONDS)
                        continue

                    latest_open_time = (
                        str(last_known_candle.get("open_time") or "")
                        if last_known_candle
                        else ""
                    )

                    ok = await _safe_send_json(
                        websocket,
                        {
                            "event": "provider_error",
                            "data": {
                                "symbol": subscription.symbol,
                                "timeframe": subscription.timeframe,
                                "message": provider_error,
                            },
                        },
                    )
                    if not ok:
                        stop_event.set()
                        break

                    ok = await _safe_send_json(
                        websocket,
                        {
                            "event": "candles_refresh",
                            "data": {
                                "symbol": subscription.symbol,
                                "timeframe": subscription.timeframe,
                                "count": 1 if last_known_candle else 0,
                                "reason": "provider_latest_failed",
                                "poll_seconds": POLL_INTERVAL_SECONDS,
                                "latest_open_time": latest_open_time,
                            },
                        },
                    )
                    if not ok:
                        stop_event.set()
                        break

                    await asyncio.sleep(POLL_INTERVAL_SECONDS)
                    continue

                quota_state.clear()

                latest_signature = _candle_signature(latest_candle)
                latest_open_time = (
                    str(latest_candle.get("open_time") or "") if latest_candle else ""
                )

                candle_changed = bool(
                    latest_candle and latest_signature and latest_signature != last_signature
                )

                logger.info(
                    "websocket_incremental_poll",
                    extra={
                        "symbol": subscription.symbol,
                        "timeframe": subscription.timeframe,
                        "latest_open_time": latest_open_time,
                        "changed": candle_changed,
                    },
                )

                if candle_changed and latest_candle:
                    ok = await _safe_send_json(
                        websocket,
                        {
                            "event": "candle_tick",
                            "data": _extract_tick_payload(
                                latest_candle,
                                symbol=subscription.symbol,
                                timeframe=subscription.timeframe,
                            ),
                        },
                    )
                    if not ok:
                        stop_event.set()
                        break

                    last_known_candle = latest_candle
                    last_signature = latest_signature

                ok = await _safe_send_json(
                    websocket,
                    {
                        "event": "candles_refresh",
                        "data": {
                            "symbol": subscription.symbol,
                            "timeframe": subscription.timeframe,
                            "count": 1 if latest_candle else 0,
                            "reason": (
                                "provider_latest_candle_updated"
                                if candle_changed
                                else "provider_poll_no_change"
                            ),
                            "poll_seconds": POLL_INTERVAL_SECONDS,
                            "latest_open_time": latest_open_time,
                        },
                    },
                )
                if not ok:
                    stop_event.set()
                    break

                await asyncio.sleep(POLL_INTERVAL_SECONDS)

    logger.info(
        "websocket_subscription_end",
        extra={
            "symbol": subscription.symbol,
            "timeframe": subscription.timeframe,
        },
    )


async def _stop_task(task: asyncio.Task | None) -> None:
    if not task:
        return

    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


@router.websocket("/ws")
async def websocket_feed(websocket: WebSocket) -> None:
    await websocket.accept()
    logger.info("websocket_connection_open")

    connection_stop_event = asyncio.Event()
    heartbeat_task = asyncio.create_task(
        _heartbeat_loop(websocket, connection_stop_event)
    )

    subscription_task: asyncio.Task | None = None
    subscription_stop_event: asyncio.Event | None = None

    try:
        connected_ok = await _safe_send_json(
            websocket,
            {
                "event": "connected",
                "data": {
                    "message": "websocket connected",
                },
            },
        )
        if not connected_ok:
            return

        while not connection_stop_event.is_set():
            raw_message = await _safe_receive_text(websocket)
            if raw_message is None:
                break

            if raw_message == "frontend_connected":
                ok = await _safe_send_json(
                    websocket,
                    {
                        "event": "echo",
                        "data": {
                            "message": "frontend_connected",
                        },
                    },
                )
                if not ok:
                    break
                continue

            try:
                payload = json.loads(raw_message)
            except json.JSONDecodeError:
                ok = await _safe_send_json(
                    websocket,
                    {
                        "event": "provider_error",
                        "data": {
                            "message": "Mensagem websocket inválida.",
                        },
                    },
                )
                if not ok:
                    break
                continue

            action = str(payload.get("action") or "").strip().lower()

            if action != "subscribe":
                ok = await _safe_send_json(
                    websocket,
                    {
                        "event": "provider_error",
                        "data": {
                            "message": f"Ação websocket não suportada: {action or '-'}",
                        },
                    },
                )
                if not ok:
                    break
                continue

            symbol = _normalize_symbol(payload.get("symbol"))
            timeframe = _normalize_timeframe(payload.get("timeframe"))
            market_type = (
                str(payload.get("market_type")).strip()
                if payload.get("market_type") is not None
                else None
            )
            catalog = (
                str(payload.get("catalog")).strip()
                if payload.get("catalog") is not None
                else None
            )

            if not symbol or not timeframe:
                ok = await _safe_send_json(
                    websocket,
                    {
                        "event": "provider_error",
                        "data": {
                            "message": "Subscrição inválida: símbolo e timeframe são obrigatórios.",
                        },
                    },
                )
                if not ok:
                    break
                continue

            if subscription_stop_event:
                subscription_stop_event.set()
            await _stop_task(subscription_task)

            subscription_stop_event = asyncio.Event()
            subscription = SubscriptionState(
                market_type=market_type,
                catalog=catalog,
                symbol=symbol,
                timeframe=timeframe,
            )

            ok = await _safe_send_json(
                websocket,
                {
                    "event": "subscribed",
                    "data": {
                        "market_type": market_type,
                        "catalog": catalog,
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "poll_seconds": POLL_INTERVAL_SECONDS,
                    },
                },
            )
            if not ok:
                break

            subscription_task = asyncio.create_task(
                _subscription_stream_loop(
                    websocket,
                    subscription_stop_event,
                    subscription,
                )
            )

    except WebSocketDisconnect:
        logger.info("websocket_connection_closed_by_client")
    except asyncio.CancelledError:
        logger.info("websocket_connection_cancelled")
        raise
    except Exception as exc:
        logger.exception("websocket_connection_unexpected_error: %s", exc)
    finally:
        connection_stop_event.set()

        if subscription_stop_event:
            subscription_stop_event.set()

        await _stop_task(subscription_task)
        await _stop_task(heartbeat_task)

        with suppress(Exception):
            await websocket.close()

        logger.info("websocket_connection_closed")