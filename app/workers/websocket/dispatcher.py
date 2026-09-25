from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any
from uuid import UUID

from aio_pika.abc import AbstractIncomingMessage
from pydantic import BaseModel

from app.events import Event
from app.workers.websocket.schemas import EventEnvelope


class EventDispatcher:
    def __init__(self):
        self._events: dict[str,tuple[type[Event], Callable[[Event], Awaitable[Any]]]] = {}


    def register(self, event_cls: type[Event]):
        def decorator(handler: Callable[[Event], Awaitable[Any]]):
            self._events[event_cls.event_type] = (event_cls, handler)
            return handler

        return decorator

    async def dispatch(self, message: AbstractIncomingMessage):
        data = EventEnvelope.model_validate_json(message.body)

        if data.event_type not in self._events:
            return

        event_cls, handler = self._events[data.event_type]

        event = event_cls.model_validate(data.payload)

        await handler(event, data)


dispatcher = EventDispatcher()