from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({
        "event": "connected",
        "data": {
            "message": "WebSocket connected successfully"
        }
    })

    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({
                "event": "echo",
                "data": {
                    "message": data
                }
            })
    except WebSocketDisconnect:
        pass