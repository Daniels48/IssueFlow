import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions.base import AppException

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request,exc: RequestValidationError) -> JSONResponse:
    errors = []

    for error in exc.errors():
        error = error.copy()

        if "ctx" in error and "error" in error["ctx"]:
            error["ctx"] = error["ctx"].copy()
            error["ctx"]["error"] = str(error["ctx"]["error"])

        errors.append(error)

    logger.warning(
        "Request validation error",
        extra={
            "path": request.url.path,
            "method": request.method,
            "query_params": dict(request.query_params),
            "errors": errors,
        },
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": errors,
        },
    )


async def app_exception_handler(request: Request,exc: AppException) -> JSONResponse:
    logger.warning(
        "Application exception",
        extra={
            "error_code": str(exc.code),
            "error_message": str(exc.message),
            "public_message": str(exc.public_message),
            "exception_status_code": exc.status_code,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.public_message,
        },
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled exception",
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
        },
    )