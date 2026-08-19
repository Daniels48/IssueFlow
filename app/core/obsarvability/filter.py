import logging

from app.core.obsarvability.contex import request_id_ctx, method_ctx, path_ctx, duration_ctx, status_code_ctx, \
    client_ip_ctx, user_agent_ctx, client_port_ctx, protocol_ctx, request_ctx, query_params_ctx, user_data_other_ctx


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        record.method = method_ctx.get()
        record.path = path_ctx.get()
        record.status_code = status_code_ctx.get()
        record.duration_ms = duration_ctx.get()
        record.version = "1.0.0"
        record.service = "IssueFlow-api"
        record.client_ip = client_ip_ctx.get()
        record.client = {
            **(user_agent_ctx.get() or {}),
            **(user_data_other_ctx.get() or {}),
        }
        record.client_port = client_port_ctx.get()
        record.protocol = protocol_ctx.get()
        record.query_params = query_params_ctx.get()
        request = request_ctx.get()

        record.user_id = getattr(request.state, "user_id", None) if request else None
        return True
