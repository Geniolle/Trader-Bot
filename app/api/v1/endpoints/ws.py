# app/api/v1/endpoints/ws.py

import asyncio
import json
from contextlib import suppress
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.settings import get_settings
from app.providers.factory import MarketDataProviderFactory

router = APIRouter()


def _is_mock_provider(provider_name: str) -> bool:
    return provider_name.strip().lower() == "mock"


def _build_provider_metadata(provider_name: str, settings_timezone: str) -> dict:
    normalized_provider = provider_name.strip().lower()
    is_mock = _is_mock_provider(normalized_provider)

    return {
        "source": normalized_provider,
        "provider": normalized_provider,
        "market_session": "simulated" if is_mock else "live",
        "timezone": settings_timezone or "UTC",
        "is_delayed": False,
        "is_mock": is_mock,
    }


def _normalize_symbol(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().upper()


def _normalize_timeframe(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower()


def _resolve_lookback_delta(timeframe: str) -> timedelta:
    normalized = timeframe.strip().lower()

    if normalized == "1m":
        return timedelta(hours=6)
    if normalized == "5m":
        return timedelta(days=1)
    if normalized == "15m":
        return timedelta(days=2)
    if normalized == "30m":
        return timedelta(days=3)
    if normalized == "45m":
        return timedelta(days=4)
    if normalized == "1h":
        return timedelta(days=7)
    if normalized == "2h":
        return timedelta(days=10)
    if normalized == "4h":
        return timedelta(days=20)
    if normalized in ("1d", "1day"):
        return timedelta(days=60)
    if normalized in ("1w", "1week"):
        return timedelta(days=365)
    if normalized in ("1mo", "1month"):
        return timedelta(days=730)

    return timedelta(days=3)


def _resolve_poll_seconds(timeframe: str) -> int:
    normalized = timeframe.strip().lower()

    if normalized == "1m":
        return 20
    if normalized == "5m":
        return 60
    if normalized == "15m":
        return 180
    if normalized == "30m":
        return 300
    if normalized == "45m":
        return 300
    if normalized == "1h":
        return 600
    if normalized == "2h":
        return 900
    if normalized == "4h":
        return 1800
    if normalized in ("1d", "1day"):
        return 3600
    if normalized in ("1w", "1week"):
        return 21600
    if normalized in ("1mo", "1month"):
        return 43200

    return 60


def _build_time_window(timeframe: str) -> tuple[datetime, datetime]:
    now_utc = datetime.now(timezone.utc)
    safe_end_at = now_utc - timedelta(minutes=5)
    safe_start_at = safe_end_at - _resolve_lookback_delta(timeframe)
    return safe_start_at, safe_end_at


def _serialize_candle(candle, provider_name: str, settings_timezone: str) -> dict:
    return {
        "id": f"{candle.symbol}:{candle.timeframe}:{candle.open_time.isoformat()}",
        "asset_id": None,
        "symbol": candle.symbol,
        "timeframe": candle.timeframe,
        "open_time": candle.open_time.astimezone(timezone.utc)
        .replace(second=0, microsecond=0)
        .isoformat(),
        "close_time": candle.close_time.astimezone(timezone.utc)
        .replace(second=0, microsecond=0)
        .isoformat(),
        "open": str(candle.open),
        "high": str(candle.high),
        "low": str(candle.low),
        "close": str(candle.close),
        "volume": str(candle.volume),
        "source": candle.source or provider_name,
        "provider": provider_name,
        "market_session": "simulated" if _is_mock_provider(provider_name) else "live",
        "timezone": settings_timezone or "UTC",
        "is_delayed": False,
        "is_mock": _is_mock_provider(provider_name),
    }


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()

    settings = get_settings()
    provider_factory = MarketDataProviderFactory()
    provider = provider_factory.get_provider(settings.market_data_provider)

    provider_name = provider.provider_name()
    provider_metadata = _build_provider_metadata(provider_name, settings.timezone)

    subscription = {
        "symbol": "AAPL",
        "timeframe": "1h",
    }

    await websocket.send_json(
        {
            "event": "connected",
            "data": {
                "message": "WebSocket connected successfully",
                "symbol": subscription["symbol"],
                "timeframe": subscription["timeframe"],
                **provider_metadata,
            },
        }
    )

    async def send_initial_candles(symbol: str, timeframe: str) -> None:
        start_at, end_at = _build_time_window(timeframe)

        try:
            candles = provider.get_historical_candles(
                symbol=symbol,
                timeframe=timeframe,
                start_at=start_at,
                end_at=end_at,
            )

            serialized_candles = [
                _serialize_candle(
                    candle=candle,
                    provider_name=provider_name,
                    settings_timezone=settings.timezone,
                )
                for candle in candles
            ]

            print(
                {
                    "event": "initial_candles_debug",
                    "status": "success",
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "count": len(serialized_candles),
                    "start_at": start_at.isoformat(),
                    "end_at": end_at.isoformat(),
                }
            )

            await websocket.send_json(
                {
                    "event": "initial_candles",
                    "data": {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "count": len(serialized_candles),
                        "candles": serialized_candles,
                        "start_at": start_at.isoformat(),
                        "end_at": end_at.isoformat(),
                        **provider_metadata,
                    },
                }
            )
        except Exception as exc:
            print(
                {
                    "event": "initial_candles_debug",
                    "status": "error",
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "start_at": start_at.isoformat(),
                    "end_at": end_at.isoformat(),
                    "error": str(exc),
                }
            )

            await websocket.send_json(
                {
                    "event": "provider_error",
                    "data": {
                        "message": str(exc),
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "start_at": start_at.isoformat(),
                        "end_at": end_at.isoformat(),
                        **provider_metadata,
                    },
                }
            )

    async def heartbeat_loop() -> None:
        counter = 0

        while True:
            poll_seconds = _resolve_poll_seconds(subscription["timeframe"])
            await asyncio.sleep(poll_seconds)
            counter += 1

            symbol = subscription["symbol"]
            timeframe = subscription["timeframe"]
            start_at, end_at = _build_time_window(timeframe)

            await websocket.send_json(
                {
                    "event": "heartbeat",
                    "data": {
                        "count": counter,
                        "message": "heartbeat from backend",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "poll_seconds": poll_seconds,
                        **provider_metadata,
                    },
                }
            )

            try:
                candles = provider.get_historical_candles(
                    symbol=symbol,
                    timeframe=timeframe,
                    start_at=start_at,
                    end_at=end_at,
                )

                if not candles:
                    await websocket.send_json(
                        {
                            "event": "provider_error",
                            "data": {
                                "message": "Provider returned no candles for the requested interval.",
                                "symbol": symbol,
                                "timeframe": timeframe,
                                "count": counter,
                                "poll_seconds": poll_seconds,
                                "start_at": start_at.isoformat(),
                                "end_at": end_at.isoformat(),
                                **provider_metadata,
                            },
                        }
                    )
                    continue

                last_candle = candles[-1]

                tick_payload = {
                    "symbol": last_candle.symbol,
                    "timeframe": last_candle.timeframe,
                    "open_time": last_candle.open_time.astimezone(timezone.utc)
                    .replace(second=0, microsecond=0)
                    .isoformat(),
                    "open": float(last_candle.open),
                    "high": float(last_candle.high),
                    "low": float(last_candle.low),
                    "close": float(last_candle.close),
                    "count": counter,
                    "poll_seconds": poll_seconds,
                    "source": last_candle.source or provider_name,
                    "provider": provider_name,
                    "market_session": "simulated" if _is_mock_provider(provider_name) else "live",
                    "timezone": settings.timezone or "UTC",
                    "is_delayed": False,
                    "is_mock": _is_mock_provider(provider_name),
                }

                print(
                    {
                        "event": "candle_tick_debug",
                        "status": "success",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "poll_seconds": poll_seconds,
                        "start_at": start_at.isoformat(),
                        "end_at": end_at.isoformat(),
                        **tick_payload,
                    }
                )

                await websocket.send_json(
                    {
                        "event": "candle_tick",
                        "data": tick_payload,
                    }
                )

            except Exception as exc:
                print(
                    {
                        "event": "candle_tick_debug",
                        "status": "error",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "poll_seconds": poll_seconds,
                        "start_at": start_at.isoformat(),
                        "end_at": end_at.isoformat(),
                        "error": str(exc),
                        "count": counter,
                        "provider": provider_name,
                    }
                )

                await websocket.send_json(
                    {
                        "event": "provider_error",
                        "data": {
                            "message": str(exc),
                            "symbol": symbol,
                            "timeframe": timeframe,
                            "count": counter,
                            "poll_seconds": poll_seconds,
                            "start_at": start_at.isoformat(),
                            "end_at": end_at.isoformat(),
                            **provider_metadata,
                        },
                    }
                )

    heartbeat_task = asyncio.create_task(heartbeat_loop())

    try:
        while True:
            raw_message = await websocket.receive_text()

            if raw_message == "frontend_connected":
                await websocket.send_json(
                    {
                        "event": "echo",
                        "data": {
                            "message": raw_message,
                            "symbol": subscription["symbol"],
                            "timeframe": subscription["timeframe"],
                            **provider_metadata,
                        },
                    }
                )
                continue

            try:
                parsed_message = json.loads(raw_message)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "event": "echo",
                        "data": {
                            "message": raw_message,
                            "symbol": subscription["symbol"],
                            "timeframe": subscription["timeframe"],
                            **provider_metadata,
                        },
                    }
                )
                continue

            action = str(parsed_message.get("action", "")).strip().lower()

            if action == "subscribe":
                next_symbol = _normalize_symbol(parsed_message.get("symbol"))
                next_timeframe = _normalize_timeframe(parsed_message.get("timeframe"))

                if not next_symbol or not next_timeframe:
                    await websocket.send_json(
                        {
                            "event": "subscription_error",
                            "data": {
                                "message": "Both symbol and timeframe are required for subscribe.",
                                "received_symbol": parsed_message.get("symbol"),
                                "received_timeframe": parsed_message.get("timeframe"),
                                **provider_metadata,
                            },
                        }
                    )
                    continue

                subscription["symbol"] = next_symbol
                subscription["timeframe"] = next_timeframe

                await websocket.send_json(
                    {
                        "event": "subscribed",
                        "data": {
                            "message": "Subscription updated successfully.",
                            "symbol": subscription["symbol"],
                            "timeframe": subscription["timeframe"],
                            "poll_seconds": _resolve_poll_seconds(subscription["timeframe"]),
                            **provider_metadata,
                        },
                    }
                )

                await send_initial_candles(
                    symbol=subscription["symbol"],
                    timeframe=subscription["timeframe"],
                )
                continue

            await websocket.send_json(
                {
                    "event": "echo",
                    "data": {
                        "message": raw_message,
                        "symbol": subscription["symbol"],
                        "timeframe": subscription["timeframe"],
                        **provider_metadata,
                    },
                }
            )

    except WebSocketDisconnect:
        pass
    finally:
        heartbeat_task.cancel()
        with suppress(asyncio.CancelledError):
            await heartbeat_task