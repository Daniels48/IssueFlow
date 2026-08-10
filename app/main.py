from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.staticfiles import StaticFiles

from app.core.exceptions import (AppException, validation_exception_handler,
    app_exception_handler, unhandled_exception_handler)
from app.infrastructure.rabbitmq.connection import RabbitConnection
from app.infrastructure.rabbitmq.publisher import RabbitPublisher
from app.router import api_router
from app.web.router import router as web_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    await RabbitPublisher.connect()

    yield

    await RabbitPublisher.close()
    await RabbitConnection.close()

app = FastAPI(lifespan=lifespan, title="issueflow")

app.mount("/static",StaticFiles(directory="app/web/static"), name="static")

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)




# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await RabbitConsumer.subscribe(
#         queue_name="email_queue",
#         routing_key="issue.created",
#         handler=email_handler,
#     )
#
#     yield
#
#     await RabbitConsumer.close()
#     await RabbitConnection.close()


app.include_router(api_router)
app.include_router(web_router)
