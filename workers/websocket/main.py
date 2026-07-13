from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.rabbitmq.connection import RabbitConnection
from app.infrastructure.rabbitmq.consumer import RabbitConsumer
from app.infrastructure.rabbitmq.publisher import RabbitPublisher
from workers.websocket.handlers.issue import issue_created_handler
from workers.websocket.router import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    await RabbitPublisher.connect()

    channel = await RabbitConsumer.subscribe(
        queue_name="ws",
        routing_key="issue.*",
        handler=issue_created_handler,
    )

    try:
        yield
    finally:
        await channel.close()
        await RabbitConnection.close()


app = FastAPI(title="IssueFlow WebSocket", lifespan=lifespan)

app.include_router(router)