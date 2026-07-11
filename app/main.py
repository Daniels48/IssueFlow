from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.rabbit.connection import RabbitConnection
from app.infrastructure.rabbit.publisher import RabbitPublisher
from app.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await RabbitConnection.connect()
    await RabbitPublisher.connect()

    yield

    await RabbitPublisher.close()
    await RabbitConnection.close()


app = FastAPI(lifespan=lifespan, title="issueflow")



@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(api_router)
