from contextlib import asynccontextmanager
from asgi_profiler import install

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.staticfiles import StaticFiles

from app.core.exceptions import (AppException, validation_exception_handler,
    app_exception_handler, unhandled_exception_handler)
from app.core.middleware import logging_middleware
from app.core.obsarvability.config import setup_logging
from app.infrastructure.rabbitmq import RabbitConnection, RabbitPublisher
from app.modules.router import api_router
from app.web.router import router as web_router


setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await RabbitPublisher.connect()

    yield

    await RabbitPublisher.close()
    await RabbitConnection.close()


app = FastAPI(lifespan=lifespan, title="issueflow") #app

install(app)


# --------------------------- STATIC -----------------------------
app.mount("/static",StaticFiles(directory="app/web/static"), name="static")


# ------------------------- MIDDLEWARE ---------------------------
app.middleware("http")(logging_middleware)


# ---------------------- EXCEPTION HANDLERS ----------------------
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


# ---------------------- ROUTES ----------------------
app.include_router(api_router)
app.include_router(web_router)


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