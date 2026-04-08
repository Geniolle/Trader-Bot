import json
from datetime import datetime, timedelta

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.storage.database import SessionLocal
from app.storage.repositories.candle_queries import CandleQueryRepository

router = APIRouter(tags=["ws"])


def normalize_symbol(value: str | None) -> str:
    return (value or "").strip().upper()


def normalize_timeframe(value: str | None) -> str:
    normalized = (value or "").strip().lower()

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


def timeframe_to_window(timeframe: str) -> timedelta:
    mapping = {
        "1m": timedelta(hours=24),
        "3m": timedelta(hours=24),
        "5m": timedelta(hours=24),
        "15m": timedelta(days=3),
        "30m": timedelta(days=3),
        "1h": timedelta(days=15),
        "4h": timedelta(days=15),
        "1d": timedelta(days=60),
    }
    return mapping.get(timeframe, timedelta(days=7))


def build_initial_candles_payload(
    symbol: str,
    timeframe: str,
) -> list[dict]:
    now = datetime.utcnow()
    start_at = now - timeframe_to_window(timeframe)

    session = SessionLocal()
    try:
        rows = CandleQueryRepository().list_by_filters(
            session=session,
            symbol=symbol,
            timeframe=timeframe,
            start_at=start_at,
            end_at=now,
            limit=5000,
        )

        return [
            {
                "id": row.id,
                "asset_id": row.asset_id,
                "symbol": row.symbol,
                "timeframe": row.timeframe,
                "open_time": row.open_time.isoformat(),
                "close_time": row.close_time.isoformat(),
                "open": str(row.open),
                "high": str(row.high),
                "low": str(row.low),
                "close": str(row.close),
                "volume": str(row.volume),
                "source": row.source,
            }
            for row in rows
        ]
    finally:
        session.close()


@router.websocket("/ws")
async def websocket_feed(websocket: WebSocket) -> None:
    await websocket.accept()

    await websocket.send_json(
        {
            "event": "connected",
            "data": {
                "message": "websocket_connected",
            },
        }
    )

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

            action = str(payload.get("action") or "").strip().lower()

            if action != "subscribe":
                await websocket.send_json(
                    {
                        "event": "provider_error",
                        "data": {
                            "message": f"Ação websocket não suportada: {action or '-'}",
                        },
                    }
                )
                continue

            symbol = normalize_symbol(payload.get("symbol"))
            timeframe = normalize_timeframe(payload.get("timeframe"))

            if not symbol or not timeframe:
                await websocket.send_json(
                    {
                        "event": "provider_error",
                        "data": {
                            "message": "Subscrição inválida: símbolo e timeframe são obrigatórios.",
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
                        "market_type": payload.get("market_type"),
                        "catalog": payload.get("catalog"),
                    },
                }
            )

            candles = build_initial_candles_payload(
                symbol=symbol,
                timeframe=timeframe,
            )

            await websocket.send_json(
                {
                    "event": "initial_candles",
                    "data": {
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "candles": candles,
                    },
                }
            )

    except WebSocketDisconnect:
        return