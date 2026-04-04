# app/api/v1/endpoints/ws.py

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from uvicorn.protocols.utils import ClientDisconnected

router = APIRouter()
logger = logging.getLogger(__name__)

TWELVEDATA_BASE_URL = "https://api.twelvedata.com/time_series"


# ============================================================================
# HELPERS
# ============================================================================

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_symbol(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().upper()


def normalize_timeframe(value: Any) -> str:
    if not isinstance(value, str):
        return ""

    normalized = value.strip().lower()
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


def timeframe_to_provider_interval(timeframe: str) -> str:
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
    return mapping.get(normalize_timeframe(timeframe), timeframe)


def default_window_for_timeframe(timeframe: str) -> timedelta:
    normalized = normalize_timeframe(timeframe)

    if normalized in {"1m", "3m", "5m"}:
        return timedelta(days=1)
    if normalized in {"15m", "30m"}:
        return timedelta(days=3)
    if normalized in {"1h", "4h"}:
        return timedelta(days=15)

    return timedelta(days=60)


def extract_error_message(exc: Exception) -> str:
    text = str(exc).strip()
    return text or exc.__class__.__name__


def is_provider_rate_limit_error(exc: Exception) -> bool:
    message = extract_error_message(exc).lower()
    return "429" in message or "rate limit" in message or "api credits" in message


def map_symbol_to_twelvedata(
    *,
    symbol: str,
    market_type: str | None = None,
    catalog: str | None = None,
) -> str:
    normalized_symbol = normalize_symbol(symbol)
    market_type_value = (market_type or "").strip().lower()
    catalog_value = (catalog or "").strip().lower()

    if market_type_value == "forex":
        if "/" in normalized_symbol:
            return normalized_symbol
        if len(normalized_symbol) == 6:
            return f"{normalized_symbol[:3]}/{normalized_symbol[3:]}"
        return normalized_symbol

    if market_type_value in {"cripto", "crypto"}:
        if catalog_value == "spot":
            if normalized_symbol.endswith("USDT") and len(normalized_symbol) > 4:
                base = normalized_symbol[:-4]
                return f"{base}/USDT"
            if normalized_symbol.endswith("USD") and len(normalized_symbol) > 3:
                base = normalized_symbol[:-3]
                return f"{base}/USD"
        return normalized_symbol

    return normalized_symbol


def parse_twelvedata_datetime_to_iso(value: str) -> str:
    raw = value.strip()

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(raw, fmt)
            parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.isoformat()
        except ValueError:
            continue

    raise RuntimeError(f"Data inválida devolvida pela Twelve Data: {value}")


def timeframe_to_timedelta(timeframe: str) -> timedelta:
    normalized = normalize_timeframe(timeframe)

    mapping = {
        "1m": timedelta(minutes=1),
        "3m": timedelta(minutes=3),
        "5m": timedelta(minutes=5),
        "15m": timedelta(minutes=15),
        "30m": timedelta(minutes=30),
        "1h": timedelta(hours=1),
        "4h": timedelta(hours=4),
        "1d": timedelta(days=1),
    }

    return mapping.get(normalized, timedelta(minutes=5))


def build_close_time_iso(open_time_iso: str, timeframe: str) -> str:
    parsed = datetime.fromisoformat(open_time_iso)
    return (parsed + timeframe_to_timedelta(timeframe)).isoformat()


def normalize_string_or_none(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


# ============================================================================
# PROVIDER
# ============================================================================

async def get_initial_candles_from_provider(
    *,
    symbol: str,
    timeframe: str,
    market_type: str | None = None,
    catalog: str | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
) -> list[dict[str, Any]]:
    api_key = os.getenv("TWELVEDATA_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("TWELVEDATA_API_KEY não configurada.")

    normalized_symbol = normalize_symbol(symbol)
    normalized_timeframe = normalize_timeframe(timeframe)
    provider_symbol = map_symbol_to_twelvedata(
        symbol=normalized_symbol,
        market_type=market_type,
        catalog=catalog,
    )
    provider_interval = timeframe_to_provider_interval(normalized_timeframe)

    params: dict[str, Any] = {
        "symbol": provider_symbol,
        "interval": provider_interval,
        "apikey": api_key,
        "format": "JSON",
        "timezone": "UTC",
        "order": "ASC",
    }

    if start_at:
        params["start_date"] = start_at.strftime("%Y-%m-%d %H:%M:%S")
    if end_at:
        params["end_date"] = end_at.strftime("%Y-%m-%d %H:%M:%S")

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(TWELVEDATA_BASE_URL, params=params)

    if response.status_code == 429:
        raise RuntimeError(f"Twelve Data API error (429): {response.text}")

    if response.status_code >= 400:
        raise RuntimeError(
            f"Twelve Data API error ({response.status_code}): {response.text}"
        )

    try:
        payload = response.json()
    except Exception as exc:
        raise RuntimeError(f"Resposta JSON inválida da Twelve Data: {exc}") from exc

    if isinstance(payload, dict) and payload.get("status") == "error":
        code = payload.get("code")
        message = payload.get("message") or "Erro desconhecido da Twelve Data."
        raise RuntimeError(f"Twelve Data API error ({code}): {message}")

    values = payload.get("values")
    if not isinstance(values, list):
        return []

    candles: list[dict[str, Any]] = []

    for index, item in enumerate(values):
        if not isinstance(item, dict):
            continue

        dt_raw = item.get("datetime")
        open_raw = item.get("open")
        high_raw = item.get("high")
        low_raw = item.get("low")
        close_raw = item.get("close")
        volume_raw = item.get("volume", "0")

        if not isinstance(dt_raw, str):
            continue

        open_time_iso = parse_twelvedata_datetime_to_iso(dt_raw)
        close_time_iso = build_close_time_iso(open_time_iso, normalized_timeframe)

        candles.append(
            {
                "id": f"{normalized_symbol}-{normalized_timeframe}-{index}-{open_time_iso}",
                "asset_id": None,
                "symbol": normalized_symbol,
                "timeframe": normalized_timeframe,
                "open_time": open_time_iso,
                "close_time": close_time_iso,
                "open": str(open_raw or "0"),
                "high": str(high_raw or "0"),
                "low": str(low_raw or "0"),
                "close": str(close_raw or "0"),
                "volume": str(volume_raw or "0"),
                "source": "twelvedata",
                "provider": "twelvedata",
                "market_session": None,
                "timezone": "UTC",
                "is_delayed": False,
                "is_mock": False,
            }
        )

    return candles


# ============================================================================
# SAFE WS HELPERS
# ============================================================================

async def safe_send_json(websocket: WebSocket, payload: dict[str, Any]) -> bool:
    try:
        if websocket.client_state != WebSocketState.CONNECTED:
            return False

        await websocket.send_json(payload)
        return True

    except (WebSocketDisconnect, ClientDisconnected):
        logger.info("WS send skipped: client already disconnected")
        return False

    except RuntimeError as exc:
        logger.info("WS runtime send skipped: %s", exc)
        return False

    except Exception as exc:
        logger.warning("WS send failed: %s", exc)
        return False


async def safe_close(
    websocket: WebSocket,
    code: int = 1000,
    reason: str | None = None,
) -> None:
    try:
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close(code=code, reason=reason)
    except Exception as exc:
        logger.debug("WS close ignored: %s", exc)


async def send_provider_error(
    websocket: WebSocket,
    *,
    symbol: str,
    timeframe: str,
    message: str,
    market_type: str | None = None,
    catalog: str | None = None,
) -> bool:
    return await safe_send_json(
        websocket,
        {
            "event": "provider_error",
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "market_type": market_type,
                "catalog": catalog,
                "message": message,
            },
        },
    )


async def send_initial_candles(
    websocket: WebSocket,
    *,
    symbol: str,
    timeframe: str,
    market_type: str | None,
    catalog: str | None,
    candles: list[dict[str, Any]],
) -> bool:
    return await safe_send_json(
        websocket,
        {
            "event": "initial_candles",
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "market_type": market_type,
                "catalog": catalog,
                "candles": candles,
            },
        },
    )


async def send_subscribed(
    websocket: WebSocket,
    *,
    symbol: str,
    timeframe: str,
    market_type: str | None,
    catalog: str | None,
) -> bool:
    return await safe_send_json(
        websocket,
        {
            "event": "subscribed",
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "market_type": market_type,
                "catalog": catalog,
            },
        },
    )


async def heartbeat_loop(
    websocket: WebSocket,
    state: dict[str, Any],
) -> None:
    counter = 0

    try:
        while True:
            await asyncio.sleep(15)
            counter += 1

            payload = {
                "event": "heartbeat",
                "data": {
                    "count": counter,
                    "message": "alive",
                    "symbol": state.get("symbol", ""),
                    "timeframe": state.get("timeframe", ""),
                },
            }

            sent = await safe_send_json(websocket, payload)
            if not sent:
                return

    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger.debug("Heartbeat loop stopped: %s", exc)


# ============================================================================
# LOAD INITIAL CANDLES
# ============================================================================

async def load_and_send_initial_candles(
    websocket: WebSocket,
    *,
    symbol: str,
    timeframe: str,
    market_type: str | None,
    catalog: str | None,
) -> None:
    normalized_symbol = normalize_symbol(symbol)
    normalized_timeframe = normalize_timeframe(timeframe)
    provider_symbol = map_symbol_to_twelvedata(
        symbol=normalized_symbol,
        market_type=market_type,
        catalog=catalog,
    )

    end_at = utc_now()
    start_at = end_at - default_window_for_timeframe(normalized_timeframe)
    provider_interval = timeframe_to_provider_interval(normalized_timeframe)

    logger.info(
        {
            "event": "twelvedata_request_debug",
            "original_symbol": normalized_symbol,
            "provider_symbol": provider_symbol,
            "timeframe": normalized_timeframe,
            "interval": provider_interval,
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
        }
    )

    try:
        candles = await get_initial_candles_from_provider(
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            market_type=market_type,
            catalog=catalog,
            start_at=start_at,
            end_at=end_at,
        )

        logger.info(
            {
                "event": "initial_candles_debug",
                "status": "ok",
                "symbol": normalized_symbol,
                "timeframe": normalized_timeframe,
                "start_at": start_at.isoformat(),
                "end_at": end_at.isoformat(),
                "count": len(candles),
            }
        )

        sent = await send_initial_candles(
            websocket,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            market_type=market_type,
            catalog=catalog,
            candles=candles,
        )

        if not sent:
            logger.info("Initial candles not sent because client disconnected")
            return

    except Exception as exc:
        error_message = extract_error_message(exc)

        logger.warning(
            {
                "event": "initial_candles_debug",
                "status": "error",
                "symbol": normalized_symbol,
                "timeframe": normalized_timeframe,
                "start_at": start_at.isoformat(),
                "end_at": end_at.isoformat(),
                "error": error_message,
            }
        )

        await send_provider_error(
            websocket,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            market_type=market_type,
            catalog=catalog,
            message=error_message,
        )

        if is_provider_rate_limit_error(exc):
            logger.warning(
                "Provider rate limit reached for %s / %s",
                normalized_symbol,
                normalized_timeframe,
            )


# ============================================================================
# ENDPOINT
# ============================================================================

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    connection_state: dict[str, Any] = {
        "symbol": "",
        "timeframe": "",
        "market_type": None,
        "catalog": None,
    }

    heartbeat_task: asyncio.Task[Any] | None = None
    accepted = False

    try:
        await websocket.accept()
        accepted = True

        connected_sent = await safe_send_json(
            websocket,
            {
                "event": "connected",
                "data": {
                    "message": "websocket_connected",
                },
            },
        )
        if not connected_sent:
            return

        heartbeat_task = asyncio.create_task(heartbeat_loop(websocket, connection_state))

        while True:
            try:
                raw_message = await websocket.receive_text()
            except WebSocketDisconnect:
                raise
            except RuntimeError as exc:
                message = str(exc)
                if "WebSocket is not connected" in message:
                    logger.info(
                        "WebSocket already closed while waiting message | symbol=%s | timeframe=%s",
                        connection_state.get("symbol", ""),
                        connection_state.get("timeframe", ""),
                    )
                    return
                raise

            if raw_message == "frontend_connected":
                sent = await safe_send_json(
                    websocket,
                    {
                        "event": "echo",
                        "data": {
                            "message": "frontend_connected",
                        },
                    },
                )
                if not sent:
                    return
                continue

            if raw_message == "ping":
                sent = await safe_send_json(
                    websocket,
                    {
                        "event": "pong",
                        "data": {
                            "message": "pong",
                        },
                    },
                )
                if not sent:
                    return
                continue

            try:
                payload = json.loads(raw_message)
            except Exception:
                sent = await safe_send_json(
                    websocket,
                    {
                        "event": "error",
                        "data": {
                            "message": "invalid_json",
                        },
                    },
                )
                if not sent:
                    return
                continue

            action = payload.get("action")

            if action != "subscribe":
                sent = await safe_send_json(
                    websocket,
                    {
                        "event": "error",
                        "data": {
                            "message": "unsupported_action",
                            "action": action,
                        },
                    },
                )
                if not sent:
                    return
                continue

            symbol = normalize_symbol(payload.get("symbol"))
            timeframe = normalize_timeframe(payload.get("timeframe"))
            market_type = normalize_string_or_none(payload.get("market_type"))
            catalog = normalize_string_or_none(payload.get("catalog"))

            logger.info(
                {
                    "event": "subscribe_debug",
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "market_type": market_type,
                    "catalog": catalog,
                }
            )

            if not symbol or not timeframe:
                sent = await safe_send_json(
                    websocket,
                    {
                        "event": "error",
                        "data": {
                            "message": "symbol_and_timeframe_are_required",
                        },
                    },
                )
                if not sent:
                    return
                continue

            connection_state["symbol"] = symbol
            connection_state["timeframe"] = timeframe
            connection_state["market_type"] = market_type
            connection_state["catalog"] = catalog

            subscribed = await send_subscribed(
                websocket,
                symbol=symbol,
                timeframe=timeframe,
                market_type=market_type,
                catalog=catalog,
            )

            if not subscribed:
                return

            await load_and_send_initial_candles(
                websocket,
                symbol=symbol,
                timeframe=timeframe,
                market_type=market_type,
                catalog=catalog,
            )

    except WebSocketDisconnect:
        logger.info(
            "WebSocket disconnected | symbol=%s | timeframe=%s",
            connection_state.get("symbol", ""),
            connection_state.get("timeframe", ""),
        )

    except ClientDisconnected:
        logger.info(
            "Client disconnected | symbol=%s | timeframe=%s",
            connection_state.get("symbol", ""),
            connection_state.get("timeframe", ""),
        )

    except RuntimeError as exc:
        message = str(exc)
        if "WebSocket is not connected" in message:
            logger.info(
                "WebSocket already closed | symbol=%s | timeframe=%s",
                connection_state.get("symbol", ""),
                connection_state.get("timeframe", ""),
            )
        else:
            logger.exception("Unexpected runtime websocket error: %s", exc)
            if accepted:
                await safe_send_json(
                    websocket,
                    {
                        "event": "error",
                        "data": {
                            "message": extract_error_message(exc),
                        },
                    },
                )

    except Exception as exc:
        logger.exception("Unexpected websocket error: %s", exc)

        if accepted:
            await safe_send_json(
                websocket,
                {
                    "event": "error",
                    "data": {
                        "message": extract_error_message(exc),
                    },
                },
            )

    finally:
        if heartbeat_task:
            heartbeat_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await heartbeat_task

        if accepted:
            await safe_close(websocket)