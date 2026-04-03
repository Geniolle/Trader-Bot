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


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()

    settings = get_settings()
    provider_factory = MarketDataProviderFactory()
    provider = provider_factory.get_provider(settings.market_data_provider)

    provider_metadata = _build_provider_metadata(
        provider.provider_name(),
        settings.timezone,
    )

    subscription = {
        "symbol": "AAPL",
        "timeframe": "1m",
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

    async def heartbeat_loop() -> None:
        counter = 0

        while True:
            counter += 1
            await asyncio.sleep(5)

            symbol = subscription["symbol"]
            timeframe = subscription["timeframe"]

            now_utc = datetime.now(timezone.utc)
            end_at = now_utc
            start_at = end_at - timedelta(hours=2)

            await websocket.send_json(
                {
                    "event": "heartbeat",
                    "data": {
                        "count": counter,
                        "message": "heartbeat from backend",
                        "symbol": symbol,
                        "timeframe": timeframe,
                        **provider_metadata,
                    },
                }
            )

            await websocket.send_json(
                {
                    "event": "candles_refresh",
                    "data": {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "reason": "scheduled_refresh",
                        "count": counter,
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
                    "source": last_candle.source or provider.provider_name(),
                    "provider": provider.provider_name(),
                    "market_session": "simulated"
                    if _is_mock_provider(provider.provider_name())
                    else "live",
                    "timezone": settings.timezone or "UTC",
                    "is_delayed": False,
                    "is_mock": _is_mock_provider(provider.provider_name()),
                }

                print(
                    {
                        "event": "candle_tick_debug",
                        "status": "success",
                        "symbol": symbol,
                        "timeframe": timeframe,
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
                        "start_at": start_at.isoformat(),
                        "end_at": end_at.isoformat(),
                        "error": str(exc),
                        "count": counter,
                        "provider": provider.provider_name(),
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
                            **provider_metadata,
                        },
                    }
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