from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.workers.websocket.auth import authenticate
from app.workers.websocket.manager import manager


router = APIRouter()


@router.websocket("/ws")    
async def websocket_endpoint(websocket: WebSocket):
    payload = await authenticate(websocket)

    if payload is None:
        return

    await manager.connect(payload.sub, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(payload.sub, websocket)