from fastapi import WebSocket, status

from app.core.exceptions import AppException
from app.modules.auth.jwt import JWTService
from app.modules.auth.schema import AccessTokenPayload


async def authenticate(websocket: WebSocket) -> AccessTokenPayload | None:
    token = websocket.cookies.get("access_token")

    if token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return None

    try:
        return JWTService.decode_access_token(token)
    except AppException:
        await websocket.close(code=4001)
        return None
    except Exception as exc:
        await websocket.close(code=4002)