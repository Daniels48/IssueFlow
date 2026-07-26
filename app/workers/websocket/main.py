from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.rabbitmq import RabbitConnection, RabbitConsumer
from app.workers.websocket.cache.redis import RedisConnection
from app.workers.websocket.dispatcher import dispatcher
from app.workers.websocket.router import router
from app.workers.websocket.service import CacheBootstrapService

import app.workers.websocket.handlers


@asynccontextmanager
async def lifespan(_: FastAPI):
    await RabbitConnection.get_connection()
    await RedisConnection.connect()
    await CacheBootstrapService.bootstrap()

    channel = await RabbitConsumer.subscribe(queue_name="ws", routing_key="#", handler=dispatcher.dispatch)

    try:
        yield
    finally:
        await channel.close()
        await RabbitConnection.close()
        await RedisConnection.close()


app = FastAPI(title="IssueFlow WebSocket", lifespan=lifespan)

app.include_router(router)