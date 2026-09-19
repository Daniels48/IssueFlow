from dataclasses import dataclass
from app.core.exceptions.codes import ErrorCode


@dataclass(frozen=True, slots=True)
class ErrorDefinition:
    status_code: int
    public_message: str


COMMON_ERRORS = {
    ErrorCode.NOT_FOUND: ErrorDefinition(404, "Not found"),
    ErrorCode.VALIDATION_ERROR: ErrorDefinition(422, "Validation error"),
    ErrorCode.BAD_REQUEST: ErrorDefinition(400, "Bad request"),
    ErrorCode.UNAUTHORIZED: ErrorDefinition(401, "Unauthorized"),
    ErrorCode.FORBIDDEN: ErrorDefinition(403, "Forbidden"),
    ErrorCode.CONFLICT: ErrorDefinition(409, "Conflict"),
    ErrorCode.PERMISSION_DENIED: ErrorDefinition(403, "Forbidden"),
    ErrorCode.TOO_MANY_REQUESTS: ErrorDefinition(429, "Too many requests"),
    ErrorCode.INTERNAL_ERROR: ErrorDefinition(500, "Internal server error"),
    ErrorCode.SERVICE_UNAVAILABLE: ErrorDefinition(503, "Service unavailable"),
}

AUTH_ERRORS = {
    ErrorCode.INVALID_TOKEN: ErrorDefinition(403, "Forbidden"),
    ErrorCode.TOKEN_EXPIRED: ErrorDefinition(403, "Forbidden"),
    ErrorCode.INVALID_TOKEN_TYPE: ErrorDefinition(403, "Forbidden"),
    ErrorCode.REFRESH_TOKEN_NOT_FOUND: ErrorDefinition(403, "Forbidden"),
    ErrorCode.USERNAME_NOT_FOUND: ErrorDefinition(403,"Invalid credentials"),
    ErrorCode.PASSWORD_INVALID: ErrorDefinition(403,"Invalid credentials"),
}

SESSION_ERRORS = {
    ErrorCode.SESSION_EXPIRED: ErrorDefinition(403,"Forbidden"),
    ErrorCode.SESSION_NOT_FOUND: ErrorDefinition( 403,"Forbidden"),
    ErrorCode.SESSION_REVOKED: ErrorDefinition(403,"Forbidden"),
}

USER_ERRORS = {
    ErrorCode.USER_NOT_FOUND: ErrorDefinition(404,"Not found"),
    ErrorCode.USER_NOT_ACTIVE: ErrorDefinition(403,"Forbidden"),
    ErrorCode.EMAIL_ALREADY_EXISTS: ErrorDefinition(409,"Email already exists"),
    ErrorCode.USERNAME_TAKEN: ErrorDefinition(409,"Conflict"),
}

VERIFICATION_ERRORS = {
    ErrorCode.EMAIL_VERIFIED_ALREADY: ErrorDefinition(409,"Email already verified"),
    ErrorCode.INVALID_EMAIL_RESET_CODE: ErrorDefinition(400,"Invalid email reset code"),
    ErrorCode.INVALID_EMAIL_VERIFY_CODE: ErrorDefinition(400, "Invalid email verification code"),
    ErrorCode.NEW_EMAIL_SAME: ErrorDefinition(400,"New email must be different"),

    ErrorCode.INVALID_PASSWORD_RESET_CODE: ErrorDefinition(400,"Invalid password reset code"),
    ErrorCode.INVALID_PASSWORD_RESET_TOKEN: ErrorDefinition(400,"Invalid password reset token"),
    ErrorCode.NEW_PASSWORD_SAME: ErrorDefinition(400,"New password must be different"),
}

COMMENT_ERRORS = {
    ErrorCode.COMMENT_NOT_FOUND: ErrorDefinition(404, "Comment not found"),
    ErrorCode.PARENT_COMMENT_NOT_FOUND: ErrorDefinition(404, "Parent comment not found"),
    ErrorCode.PARENT_COMMENT_INVALID: ErrorDefinition(404, "Parent comment invalid"),

}

ISSUE_ERRORS = {
    ErrorCode.ISSUE_NOT_FOUND: ErrorDefinition(404, "Issue not found"),
    ErrorCode.ISSUE_ASSIGNED_NOT_FOUND: ErrorDefinition(404, "Issue assigned not found"),
    ErrorCode.INVALID_STATUS_TRANSITION: ErrorDefinition(400,"Invalid status transition"),
    ErrorCode.ISSUE_CLOSED: ErrorDefinition(403,"Forbidden"),
    ErrorCode.ISSUE_ALREADY_CLOSED: ErrorDefinition(403,"Forbidden"),
    ErrorCode.ISSUE_NOT_CLOSED: ErrorDefinition(403,"Forbidden"),
}

PROJECT_ERRORS = {
    ErrorCode.PROJECT_NOT_FOUND: ErrorDefinition(404, "Project not found"),
}

MEMBER_ERRORS = {
    ErrorCode.USER_IS_NOT_A_PROJECT_MEMBER: ErrorDefinition(403,"Forbidden"),
    ErrorCode.MEMBER_ALREADY_IN_PROJECT: ErrorDefinition(403,"Forbidden"),
}


ERROR_REGISTRY: dict[ErrorCode, ErrorDefinition] = {
    **COMMON_ERRORS,
    **AUTH_ERRORS,
    **SESSION_ERRORS,
    **USER_ERRORS,
    **VERIFICATION_ERRORS,
    **COMMENT_ERRORS,
    **ISSUE_ERRORS,
    **MEMBER_ERRORS,

}