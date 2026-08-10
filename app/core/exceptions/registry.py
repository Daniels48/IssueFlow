from dataclasses import dataclass
from app.core.exceptions.codes import ErrorCode


@dataclass(frozen=True, slots=True)
class ErrorDefinition:
    status_code: int
    public_message: str


ERROR_REGISTRY: dict[ErrorCode, ErrorDefinition] = {
    ErrorCode.NOT_FOUND: ErrorDefinition(
        status_code=404,
        public_message="Not found",
    ),

    ErrorCode.VALIDATION_ERROR: ErrorDefinition(
        status_code=422,
        public_message="Validation error",
    ),

    ErrorCode.BAD_REQUEST: ErrorDefinition(
        status_code=400,
        public_message="Bad request",
    ),

    ErrorCode.UNAUTHORIZED: ErrorDefinition(
        status_code=401,
        public_message="Unauthorized",
    ),

    ErrorCode.FORBIDDEN: ErrorDefinition(
        status_code=403,
        public_message="Forbidden",
    ),

    ErrorCode.INVALID_TOKEN: ErrorDefinition(
        status_code=403,
        public_message="Forbidden",
    ),

    ErrorCode.TOKEN_EXPIRED: ErrorDefinition(
        status_code=403,
        public_message="Forbidden",
    ),

    ErrorCode.INVALID_TOKEN_TYPE: ErrorDefinition(
        status_code=403,
        public_message="Forbidden",
    ),

    ErrorCode.REFRESH_TOKEN_NOT_FOUND: ErrorDefinition(
        status_code=403,
        public_message="Forbidden",
    ),

    ErrorCode.SESSION_EXPIRED: ErrorDefinition(
        status_code=403,
        public_message="Forbidden",
    ),

    ErrorCode.SESSION_NOT_FOUND: ErrorDefinition(
        status_code=403,
        public_message="Forbidden",
    ),

    ErrorCode.SESSION_REVOKED: ErrorDefinition(
        status_code=403,
        public_message="Forbidden",
    ),

    ErrorCode.USER_NOT_FOUND: ErrorDefinition(
        status_code=404,
        public_message="Not found",
    ),

    ErrorCode.USER_NOT_ACTIVE: ErrorDefinition(
        status_code=403,
        public_message="Forbidden",
    ),

    ErrorCode.EMAIL_ALREADY_EXISTS: ErrorDefinition(
        status_code=409,
        public_message="Conflict",
    ),

    ErrorCode.USERNAME_TAKEN: ErrorDefinition(
        status_code=409,
        public_message="Conflict",
    ),

    ErrorCode.USERNAME_NOT_FOUND: ErrorDefinition(
        status_code=403,
        public_message="Invalid credentials",
    ),

    ErrorCode.PASSWORD_INVALID: ErrorDefinition(
        status_code=403,
        public_message="Invalid credentials",
    ),

    ErrorCode.INVALID_EMAIL_CODE: ErrorDefinition(
        status_code=400,
        public_message="Bad request",
    ),

    ErrorCode.EMAIL_CODE_EXPIRED: ErrorDefinition(
        status_code=400,
        public_message="Bad request",
    ),

    ErrorCode.INVALID_RESET_CODE: ErrorDefinition(
        status_code=400,
        public_message="Bad request",
    ),

    ErrorCode.RESET_CODE_EXPIRED: ErrorDefinition(
        status_code=400,
        public_message="Bad request",
    ),

    ErrorCode.PERMISSION_DENIED: ErrorDefinition(
        status_code=403,
        public_message="Forbidden",
    ),

    ErrorCode.CONFLICT: ErrorDefinition(
        status_code=409,
        public_message="Conflict",
    ),

    ErrorCode.TOO_MANY_REQUESTS: ErrorDefinition(
        status_code=429,
        public_message="Too many requests",
    ),

    ErrorCode.INTERNAL_ERROR: ErrorDefinition(
        status_code=500,
        public_message="Internal server error",
    ),
}