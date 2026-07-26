import asyncio
from collections import defaultdict
from typing import Iterable
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

    async def disconnect_user(self,user_public_id: UUID,) -> None:
        sockets = self._connections.pop(user_public_id, set())

        for websocket in sockets:
            await websocket.close()

    async def send_to_user(self,user_public_id: UUID,message: dict) -> None:
        sockets = self._connections.get(user_public_id)

        if not sockets:
            return

        for websocket in tuple(sockets):
            try:
                await websocket.send_json(message)
            except Exception:
                await self.disconnect(user_public_id, websocket)

    async def send_to_users(self,users: Iterable[UUID], message: dict) -> None:
        tasks = (self.send_to_user(user_public_id, message) for user_public_id in users)
        await asyncio.gather(*tasks)

    async def broadcast(self, message: dict) -> None:
        tasks = (
            self._safe_send(user_public_id, websocket, message)
            for user_public_id, sockets in self._connections.items()
            for websocket in tuple(sockets)
        )

        await asyncio.gather(*tasks)

    async def _safe_send(self,user_public_id: UUID, websocket: WebSocket, message: dict) -> None:
        try:
            await websocket.send_json(message)
        except Exception:
            await self.disconnect(user_public_id, websocket)




manager = ConnectionManager()