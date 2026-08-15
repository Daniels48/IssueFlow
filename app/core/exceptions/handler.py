from fastapi.exceptions import RequestValidationError

from app.core.exceptions.base import AppException
from fastapi.responses import JSONResponse
from fastapi import Request


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # logger.warning(
    #     "Request validation error",
    #     extra={
    #         "path": request.url.path,
    #         "method": request.method,
    #         "errors": exc.errors(),
    #     },
    # )
    print("VALIDATION ERROR:")
    print(exc.errors())

    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
        },
    )
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
        },
    )




async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    # logger.error(
    #     "Application error",
    #     extra={
    #         "error_code": exc.code,
    #         "error_message": exc.message,
    #         "status_code": exc.status_code,
    #         "path": request.url.path,
    #     },
    # )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.public_message,
        },
    )

async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # logger.exception(
    #     "Unhandled exception",
    #     extra={
    #         "path": request.url.path,
    #     },
    # )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
        },
    )