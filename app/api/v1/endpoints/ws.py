# app/api/v1/endpoints/ws.py

import json
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.settings import get_settings
from app.providers.factory import MarketDataProviderFactory
from app.storage.database import SessionLocal
from app.storage.repositories.candle_queries import CandleQueryRepository
from app.storage.repositories.candle_repository import CandleRepository

router = APIRouter(tags=["ws"])


def _serialize_candle(candle) -> dict:
    return {
        "id": getattr(candle, "id", None),
        "asset_id": getattr(candle, "asset_id", None),
        "symbol": getattr(candle, "symbol", None),
        "timeframe": getattr(candle, "timeframe", None),
        "open_time": candle.open_time.isoformat() if candle.open_time else None,
        "close_time": candle.close_time.isoformat() if candle.close_time else None,
        "open": str(candle.open),
        "high": str(candle.high),
        "low": str(candle.low),
        "close": str(candle.close),
        "volume": str(candle.volume),
        "source": getattr(candle, "source", None),
    }


@router.websocket("/ws")
async def websocket_feed(websocket: WebSocket) -> None:
    await websocket.accept()

    await websocket.send_json(
        {
            "event": "connected",
            "data": {
                "message": "websocket connected",
            },
        }
    )

    session = SessionLocal()

    try:
        while True:
            raw_message = await websocket.receive_text()

            if raw_message == "frontend_connected":
                await websocket.send_json(
                    {
                        "event": "echo",
                        "data": {
                            "message": "frontend_connected",
                        },
                    }
                )
                continue

            try:
                payload = json.loads(raw_message)
            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "event": "provider_error",
                        "data": {
                            "message": "Mensagem websocket inválida.",
                        },
                    }
                )
                continue

            action = str(payload.get("action", "")).strip().lower()

            if action != "subscribe":
                await websocket.send_json(
                    {
                        "event": "provider_error",
                        "data": {
                            "message": f"Ação websocket não suportada: {action}",
                        },
                    }
                )
                continue

            symbol = str(payload.get("symbol", "")).strip().upper()
            timeframe = str(payload.get("timeframe", "")).strip().lower()

            if not symbol or not timeframe:
                await websocket.send_json(
                    {
                        "event": "provider_error",
                        "data": {
                            "message": "Subscrição inválida: symbol e timeframe são obrigatórios.",
                            "symbol": symbol,
                            "timeframe": timeframe,
                        },
                    }
                )
                continue

            await websocket.send_json(
                {
                    "event": "subscribed",
                    "data": {
                        "symbol": symbol,
                        "timeframe": timeframe,
                    },
                }
            )

            end_at = datetime.now(timezone.utc).replace(tzinfo=None)
            start_at = end_at - timedelta(days=1)

            rows = CandleQueryRepository().list_by_filters(
                session=session,
                symbol=symbol,
                timeframe=timeframe,
                start_at=start_at,
                end_at=end_at,
                limit=5000,
            )

            if not rows:
                settings = get_settings()

                try:
                    provider = MarketDataProviderFactory().get_provider(
                        settings.market_data_provider
                    )
                    candles = provider.get_historical_candles(
                        symbol=symbol,
                        timeframe=timeframe,
                        start_at=start_at,
                        end_at=end_at,
                    )

                    if candles:
                        CandleRepository().save_many(session, candles)
                        rows = CandleQueryRepository().list_by_filters(
                            session=session,
                            symbol=symbol,
                            timeframe=timeframe,
                            start_at=start_at,
                            end_at=end_at,
                            limit=5000,
                        )
                except Exception as exc:
                    await websocket.send_json(
                        {
                            "event": "provider_error",
                            "data": {
                                "message": f"Erro ao obter candles do provider: {exc}",
                                "symbol": symbol,
                                "timeframe": timeframe,
                            },
                        }
                    )
                    continue

            await websocket.send_json(
                {
                    "event": "initial_candles",
                    "data": {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "candles": [_serialize_candle(row) for row in rows],
                        "start_at": start_at.isoformat(),
                        "end_at": end_at.isoformat(),
                    },
                }
            )

            await websocket.send_json(
                {
                    "event": "heartbeat",
                    "data": {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "count": 1,
                        "message": "subscription active",
                    },
                }
            )

    except WebSocketDisconnect:
        pass
    finally:
        session.close()