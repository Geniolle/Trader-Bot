import asyncio
from contextlib import suppress

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