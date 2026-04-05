# app/api/v1/endpoints/ws.py

from __future__ import annotations

import asyncio
import contextlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from uvicorn.protocols.utils import ClientDisconnected

from app.services.candle_sync import CandleSyncService
from app.storage.database import SessionLocal

router = APIRouter()
logger = logging.getLogger(__name__)


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


def normalize_string_or_none(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def normalize_market_type(value: Any) -> str | None:
    normalized = normalize_string_or_none(value)
    if normalized is None:
        return None
    return normalized.strip().lower()


def normalize_catalog(value: Any) -> str | None:
    normalized = normalize_string_or_none(value)
    if normalized is None:
        return None
    return normalized.strip().lower()


def should_skip_provider_sync(
    market_type: str | None,
    catalog: str | None,
) -> bool:
    normalized_market_type = normalize_market_type(market_type)
    normalized_catalog = normalize_catalog(catalog)

    return normalized_market_type == "crypto" and normalized_catalog == "spot"


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


def refresh_poll_seconds_for_timeframe(timeframe: str) -> int:
    normalized = normalize_timeframe(timeframe)

    if normalized == "1m":
        return 30
    if normalized in {"3m", "5m"}:
        return 60
    if normalized in {"15m", "30m"}:
        return 180
    if normalized == "1h":
        return 300
    if normalized == "4h":
        return 900

    return 1800


def extract_error_message(exc: Exception) -> str:
    text = str(exc).strip()
    return text or exc.__class__.__name__


def is_provider_rate_limit_error(exc: Exception) -> bool:
    message = extract_error_message(exc).lower()
    return "429" in message or "rate limit" in message or "api credits" in message


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


async def send_candles_refresh(
    websocket: WebSocket,
    *,
    symbol: str,
    timeframe: str,
    market_type: str | None,
    catalog: str | None,
    count: int,
    reason: str,
    poll_seconds: int,
    start_at: datetime,
    end_at: datetime,
) -> bool:
    return await safe_send_json(
        websocket,
        {
            "event": "candles_refresh",
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "market_type": market_type,
                "catalog": catalog,
                "count": count,
                "reason": reason,
                "poll_seconds": poll_seconds,
                "start_at": start_at.replace(tzinfo=timezone.utc).isoformat(),
                "end_at": end_at.replace(tzinfo=timezone.utc).isoformat(),
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


def candle_to_ws_dict(candle) -> dict[str, Any]:
    return {
        "id": f"{candle.symbol}-{candle.timeframe}-{candle.open_time.isoformat()}",
        "asset_id": candle.asset_id,
        "symbol": candle.symbol,
        "timeframe": candle.timeframe,
        "open_time": candle.open_time.replace(tzinfo=timezone.utc).isoformat(),
        "close_time": candle.close_time.replace(tzinfo=timezone.utc).isoformat(),
        "open": str(candle.open),
        "high": str(candle.high),
        "low": str(candle.low),
        "close": str(candle.close),
        "volume": str(candle.volume),
        "source": candle.source,
        "provider": candle.source,
        "market_session": None,
        "timezone": "UTC",
        "is_delayed": False,
        "is_mock": False,
    }


async def load_and_send_initial_candles(
    websocket: WebSocket,
    *,
    symbol: str,
    timeframe: str,
    market_type: str | None,
    catalog: str | None,
) -> bool:
    normalized_symbol = normalize_symbol(symbol)
    normalized_timeframe = normalize_timeframe(timeframe)
    normalized_market_type = normalize_market_type(market_type)
    normalized_catalog = normalize_catalog(catalog)

    end_at = utc_now()
    start_at = end_at - default_window_for_timeframe(normalized_timeframe)
    provider_interval = timeframe_to_provider_interval(normalized_timeframe)

    logger.info(
        {
            "event": "sync_request_debug",
            "symbol": normalized_symbol,
            "timeframe": normalized_timeframe,
            "market_type": normalized_market_type,
            "catalog": normalized_catalog,
            "interval": provider_interval,
            "start_at": start_at.isoformat(),
            "end_at": end_at.isoformat(),
        }
    )

    if should_skip_provider_sync(normalized_market_type, normalized_catalog):
        logger.info(
            {
                "event": "initial_candles_debug",
                "status": "skipped",
                "symbol": normalized_symbol,
                "timeframe": normalized_timeframe,
                "market_type": normalized_market_type,
                "catalog": normalized_catalog,
                "reason": "crypto_spot_sync_disabled_for_provider",
                "start_at": start_at.isoformat(),
                "end_at": end_at.isoformat(),
            }
        )
        return True

    session = SessionLocal()
    service = CandleSyncService()

    try:
        result = service.get_or_sync_candles(
            session=session,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            start_at=start_at,
            end_at=end_at,
            market_type=normalized_market_type,
            catalog=normalized_catalog,
        )

        logger.info(
            {
                "event": "initial_candles_debug",
                "status": "ok",
                "symbol": normalized_symbol,
                "timeframe": normalized_timeframe,
                "source": result.source,
                "cache_hit": result.cache_hit,
                "db_hit": result.db_hit,
                "provider_hit": result.provider_hit,
                "missing_filled": result.missing_filled,
                "newly_persisted_count": result.newly_persisted_count,
                "count": len(result.candles),
                "start_at": result.requested_start_at.isoformat(),
                "end_at": result.requested_end_at.isoformat(),
            }
        )

        payload_candles = [candle_to_ws_dict(item) for item in result.candles]

        sent = await send_initial_candles(
            websocket,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            market_type=normalized_market_type,
            catalog=normalized_catalog,
            candles=payload_candles,
        )

        return bool(sent)

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

        if is_provider_rate_limit_error(exc):
            service.notify_rate_limit(cooldown_seconds=300)
            logger.warning(
                "Provider rate limit reached for %s / %s",
                normalized_symbol,
                normalized_timeframe,
            )

        await send_provider_error(
            websocket,
            symbol=normalized_symbol,
            timeframe=normalized_timeframe,
            market_type=normalized_market_type,
            catalog=normalized_catalog,
            message=error_message,
        )
        return False

    finally:
        session.close()


async def incremental_refresh_loop(
    websocket: WebSocket,
    state: dict[str, Any],
) -> None:
    try:
        while True:
            symbol = normalize_symbol(state.get("symbol"))
            timeframe = normalize_timeframe(state.get("timeframe"))
            market_type = normalize_market_type(state.get("market_type"))
            catalog = normalize_catalog(state.get("catalog"))

            if not symbol or not timeframe:
                await asyncio.sleep(2)
                continue

            poll_seconds = refresh_poll_seconds_for_timeframe(timeframe)
            await asyncio.sleep(poll_seconds)

            if should_skip_provider_sync(market_type, catalog):
                logger.debug(
                    {
                        "event": "candles_refresh_debug",
                        "status": "skipped",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "market_type": market_type,
                        "catalog": catalog,
                        "reason": "crypto_spot_sync_disabled_for_provider",
                        "poll_seconds": poll_seconds,
                    }
                )
                continue

            end_at = utc_now()
            start_at = end_at - default_window_for_timeframe(timeframe)

            session = SessionLocal()
            service = CandleSyncService()

            try:
                result = service.get_or_sync_candles(
                    session=session,
                    symbol=symbol,
                    timeframe=timeframe,
                    start_at=start_at,
                    end_at=end_at,
                    market_type=market_type,
                    catalog=catalog,
                )

                if result.newly_persisted_count > 0:
                    sent = await send_candles_refresh(
                        websocket,
                        symbol=symbol,
                        timeframe=timeframe,
                        market_type=market_type,
                        catalog=catalog,
                        count=result.newly_persisted_count,
                        reason="reload_incremental_sync",
                        poll_seconds=poll_seconds,
                        start_at=result.requested_start_at,
                        end_at=result.requested_end_at,
                    )
                    if not sent:
                        return

                    logger.info(
                        {
                            "event": "candles_refresh_debug",
                            "symbol": symbol,
                            "timeframe": timeframe,
                            "newly_persisted_count": result.newly_persisted_count,
                            "poll_seconds": poll_seconds,
                            "source": result.source,
                        }
                    )

            except Exception as exc:
                error_message = extract_error_message(exc)

                if is_provider_rate_limit_error(exc):
                    service.notify_rate_limit(cooldown_seconds=300)

                sent = await send_provider_error(
                    websocket,
                    symbol=symbol,
                    timeframe=timeframe,
                    market_type=market_type,
                    catalog=catalog,
                    message=error_message,
                )
                if not sent:
                    return

            finally:
                session.close()

    except asyncio.CancelledError:
        raise
    except Exception as exc:
        logger.debug("Incremental refresh loop stopped: %s", exc)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    connection_state: dict[str, Any] = {
        "symbol": "",
        "timeframe": "",
        "market_type": None,
        "catalog": None,
    }

    heartbeat_task: asyncio.Task[Any] | None = None
    refresh_task: asyncio.Task[Any] | None = None
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
            market_type = normalize_market_type(payload.get("market_type"))
            catalog = normalize_catalog(payload.get("catalog"))

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

            if refresh_task:
                refresh_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await refresh_task
                refresh_task = None

            subscribed = await send_subscribed(
                websocket,
                symbol=symbol,
                timeframe=timeframe,
                market_type=market_type,
                catalog=catalog,
            )

            if not subscribed:
                return

            initial_sent = await load_and_send_initial_candles(
                websocket,
                symbol=symbol,
                timeframe=timeframe,
                market_type=market_type,
                catalog=catalog,
            )
            if not initial_sent:
                return

            refresh_task = asyncio.create_task(
                incremental_refresh_loop(websocket, connection_state)
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
        if refresh_task:
            refresh_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await refresh_task

        if heartbeat_task:
            heartbeat_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await heartbeat_task

        if accepted:
            await safe_close(websocket)