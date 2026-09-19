import logging
import time

from fastapi import Request
from starlette.responses import Response

from app.core.obsarvability.contex import set_http_context, request_ctx, set_context_after_request, \
    clear_request_context

logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    request_id = set_http_context(request)

    request_ctx.set(request)

    response: Response | None = None
    error: Exception | None = None

    try:
        response = await call_next(request)
        return response

    except Exception as exc:
        error = exc
        raise

    finally:
        status_code = response.status_code if response else 500

        set_context_after_request(start_time, status_code)

        if error:
            level = logging.ERROR
            event = "http_request_failed"
        elif status_code >= 500:
            level = logging.ERROR
            event = "http_server_error"
        elif status_code >= 400:
            level = logging.WARNING
            event = "http_client_error"
        else:
            level = logging.INFO
            event = "http_request_completed"

        logger.log(
            level,
            "HTTP request completed",
            extra={"event": event},
        )

        if response:
            response.headers["X-Request-ID"] = request_id

        clear_request_context()
