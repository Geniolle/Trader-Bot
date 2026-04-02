import asyncio
from contextlib import suppress
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()

    await websocket.send_json(
        {
            "event": "connected",
            "data": {
                "message": "WebSocket connected successfully",
            },
        }
    )

    async def heartbeat_loop() -> None:
        counter = 0
        base_price = 248.50

        while True:
            counter += 1
            await asyncio.sleep(5)

            await websocket.send_json(
                {
                    "event": "heartbeat",
                    "data": {
                        "count": counter,
                        "message": "heartbeat from backend",
                    },
                }
            )

            await websocket.send_json(
                {
                    "event": "candles_refresh",
                    "data": {
                        "symbol": "AAPL",
                        "timeframe": "1m",
                        "reason": "scheduled_refresh",
                        "count": counter,
                    },
                }
            )

            open_price = round(base_price + (counter * 0.01), 5)
            high_price = round(open_price + 0.08, 5)
            low_price = round(open_price - 0.06, 5)
            close_price = round(open_price + 0.03, 5)

            await websocket.send_json(
                {
                    "event": "candle_tick",
                    "data": {
                        "symbol": "AAPL",
                        "timeframe": "1m",
                        "open_time": datetime.now(timezone.utc).isoformat(),
                        "open": open_price,
                        "high": high_price,
                        "low": low_price,
                        "close": close_price,
                        "count": counter,
                    },
                }
            )

    heartbeat_task = asyncio.create_task(heartbeat_loop())

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json(
                {
                    "event": "echo",
                    "data": {
                        "message": data,
                    },
                }
            )
    except WebSocketDisconnect:
        pass
    finally:
        heartbeat_task.cancel()
        with suppress(asyncio.CancelledError):
            await heartbeat_task