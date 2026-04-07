from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.realtime_ws import realtime_ws_manager

router = APIRouter(tags=["ws"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await realtime_ws_manager.connect(websocket)

    try:
        while True:
            message = await websocket.receive_text()
            await realtime_ws_manager.handle_message(websocket, message)
    except WebSocketDisconnect:
        await realtime_ws_manager.disconnect(websocket)
    except Exception:
        await realtime_ws_manager.disconnect(websocket)
        raise