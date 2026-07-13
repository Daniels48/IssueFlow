from collections import defaultdict
from uuid import UUID

from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self._connections: dict[UUID, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_public_id: UUID, websocket: WebSocket) -> None:
        await websocket.accept()

        self._connections[user_public_id].add(websocket)

    async def disconnect(self, user_public_id: UUID,websocket: WebSocket) -> None:
        connections = self._connections.get(user_public_id)

        if connections is None:
            return

        connections.discard(websocket)

        if not connections:
            self._connections.pop(user_public_id, None)

    async def send_to_user(self, user_public_id: UUID,message: dict) -> None:
        connections = self._connections.get(user_public_id)

        if connections is None:
            return

        disconnected = []

        for websocket in connections:
            try:
                await websocket.send_json(message)

            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            connections.discard(websocket)

        if not connections:
            self._connections.pop(user_public_id, None)

    async def broadcast(self, message: dict) -> None:
        for connections in self._connections.values():
            for websocket in connections:
                await websocket.send_json(message)


manager = ConnectionManager()