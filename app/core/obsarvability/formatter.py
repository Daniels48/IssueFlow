from datetime import datetime, timezone

from pythonjsonlogger import json


class CustomJsonFormatter(json.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        timestamp = timestamp.replace("+00:00", "Z")

        exc_info = record.exc_info

        log_record.clear()

        log_record["timestamp"] = timestamp

        log_record["message"] = record.getMessage()

        event = getattr(record, "event", None)

        if event:
            log_record["event"] = event

        log = {
            "level": record.levelname,
            "logger": record.name,
        }
        log_record["log"] = log

        service = {"name": getattr(record, "service", None), "version": getattr(record, "version", None)}

        log_record["service"] = service

        trace = {
            "request_id": getattr(record, "request_id", None),
            "user_id": getattr(record, "user_id", None),
        }

        if any(trace.values()):
            log_record["trace"] = trace

        client = getattr(record, "client", None)

        if client:
            log_record["client"] = client

        client_info = getattr(record, "client_info", None)

        if client_info:
            log_record["client_info"] = client_info

        network = {
            "protocol": getattr(record, "protocol", None),
            "path": getattr(record, "path", None),
            "query_params": getattr(record, "query_params", None),
        }

        if any(network.values()):
            log_record["network"] = network

        http = {
            "method": getattr(record, "method", None),
            "status_code": getattr(record, "status_code", None),
            "duration_ms": getattr(record, "duration_ms", None),
            "client_ip": getattr(record, "client_ip", None),
            "client_port": getattr(record, "client_port", None),
        }

        if any(http.values()):
            log_record["http"] = http

        if exc_info:
            log_record["error"] = {
                "type": exc_info[0].__name__,
                "message": str(exc_info[1]),
                "stacktrace": self.formatException(exc_info),
            }
