import json
from collections.abc import Awaitable, Callable
from typing import Any

from aio_pika.abc import AbstractIncomingMessage

from app.events import Event


class EventDispatcher:
    def __init__(self):
        self._events: dict[
            str,
            tuple[type[Event], Callable[[Event], Awaitable[Any]]]
        ] = {}

    def register(self, event_cls: type[Event]):
        def decorator(handler: Callable[[Event], Awaitable[Any]]):
            self._events[event_cls.ROUTING_KEY] = (event_cls, handler)
            return handler

        return decorator

    async def dispatch(self, message: AbstractIncomingMessage):
        data = json.loads(message.body)

        event_type = data["type"]

        if event_type not in self._events:
            return

        event_cls, handler = self._events[event_type]

        event = event_cls.model_validate(data)

        await handler(event)


dispatcher = EventDispatcher()