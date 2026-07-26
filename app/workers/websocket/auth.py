from fastapi import WebSocket, status

from app.modules.auth.jwt import JWTService
from app.modules.auth.schemas import AccessTokenPayload


async def authenticate(websocket: WebSocket) -> AccessTokenPayload | None:
    token = websocket.cookies.get("access_token")

    if token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

    try:
        return JWTService.decode_access_token(token)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None