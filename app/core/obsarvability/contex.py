import time
import uuid
from contextvars import ContextVar

from app.core.obsarvability.utils import get_protocol, parse_user_agent, sanitize_query, get_client_info

request_id_ctx = ContextVar("request_id", default=None)
user_id_ctx = ContextVar("user_id", default=None)

method_ctx = ContextVar("method", default=None)
path_ctx = ContextVar("path", default=None)
status_code_ctx = ContextVar("status_code", default=None)
duration_ctx = ContextVar("duration_ms", default=None)

client_ip_ctx = ContextVar("client_ip", default=None)
user_agent_ctx = ContextVar("client", default=None)
user_data_other_ctx = ContextVar("user_data_other", default=None)
client_port_ctx = ContextVar("client_port", default=None)

protocol_ctx = ContextVar("protocol", default=None)
query_params_ctx = ContextVar("query_params", default=None)

request_ctx = ContextVar("request", default=None)

session_id_ctx = ContextVar("session_id", default=None)


def generate_request_id(incoming_id: str | None) -> str:
    return incoming_id or str(uuid.uuid4())


def calculate_duration(start_time: float) -> float:
    return round((time.perf_counter() - start_time) * 1000, 2)


def set_http_context(request):
    request_id = generate_request_id(request.headers.get("X-Request-ID"))
    request_id_ctx.set(request_id)

    protocol_ctx.set(get_protocol(request))
    method_ctx.set(request.method)
    path_ctx.set(request.url.path)

    client_ip_ctx.set(request.client.host if request.client else None)
    user_agent_data = parse_user_agent(request.headers.get("user-agent"))


    client_info = request.headers.get("X-Client-Info")

    client_info = get_client_info(client_info)

    user_data_other_ctx.set(client_info)

    user_agent_ctx.set(user_agent_data)
    query_params_ctx.set(sanitize_query(request.query_params))
    client_port_ctx.set(request.client.port if request.client else None)

    return request_id


def set_context_after_request(start_time, status_code=None):
    status_code_ctx.set(status_code or 200)
    duration_ctx.set(calculate_duration(start_time))


def clear_request_context():
    request_id_ctx.set(None)
    user_id_ctx.set(None)

    method_ctx.set(None)
    path_ctx.set(None)
    status_code_ctx.set(None)
    duration_ctx.set(None)

    client_ip_ctx.set(None)
    client_port_ctx.set(None)
    user_agent_ctx.set(None)

    protocol_ctx.set(None)
    query_params_ctx.set(None)
    request_ctx.set(None)
