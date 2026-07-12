from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.modules.auth.jwt import JWTService
from app.modules.auth.schemas import AccessTokenPayload
from app.modules.issue.status import IssueStatus
from workers.websocket.manager import manager

router = APIRouter()

async def authenticate(websocket: WebSocket) -> AccessTokenPayload:
    token = websocket.query_params.get("token")

    if token is None:
        await websocket.close(code=200)
        raise RuntimeError("Missing token")

    try:
        return JWTService.decode_access_token(token)
    except Exception:
        await websocket.close(200)
        raise


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    payload = await authenticate(websocket)

    await manager.connect(payload.sub, websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(payload.sub, websocket)