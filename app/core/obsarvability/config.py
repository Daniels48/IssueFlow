import logging
import logging.config
import time

from app.core.obsarvability.filter import ContextFilter
from app.core.obsarvability.formatter import CustomJsonFormatter

LOG_LEVEL = "INFO"


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"context_filter": {"()": ContextFilter}},
    "formatters": {
        "json": {"()": CustomJsonFormatter},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["context_filter"],
        },
    },
    "loggers": {
        "uvicorn.access": {
            "handlers": [],
            "level": "WARNING",
            "propagate": False,
        },
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["console"],
    },
}


def setup_logging():
    logging.Formatter.converter = time.gmtime
    logging.config.dictConfig(LOGGING_CONFIG)
