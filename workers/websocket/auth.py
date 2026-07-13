from fastapi import WebSocket, status

from app.modules.auth.jwt import JWTService
from app.modules.auth.schemas import AccessTokenPayload


async def authenticate(websocket: WebSocket) -> AccessTokenPayload:
    token = websocket.query_params.get("token")

    if token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise RuntimeError("Missing token")

    try:
        return JWTService.decode_access_token(token)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise