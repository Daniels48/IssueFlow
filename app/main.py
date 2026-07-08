from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.rabbit.connection import RabbitConnection
from app.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    await RabbitConnection.connect()

    yield

    await RabbitConnection.close()


app = FastAPI(lifespan=lifespan, title="issueflow")



@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(api_router)
