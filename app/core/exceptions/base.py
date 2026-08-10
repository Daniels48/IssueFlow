from app.core.exceptions.codes import ErrorCode
from app.core.exceptions.registry import ERROR_REGISTRY


class AppException(Exception):
    def __init__(self, code: ErrorCode, message: str):
        definition = ERROR_REGISTRY[code]

        self.code = code
        self.message = message

        self.status_code = definition.status_code
        self.public_message = definition.public_message

        super().__init__(message)