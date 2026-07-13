from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from workers.websocket.auth import authenticate
from workers.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    payload = await authenticate(websocket)

    await manager.connect(payload.sub, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(payload.sub, websocket)