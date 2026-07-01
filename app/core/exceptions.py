class AppException(Exception):
    """Base application exception."""

class EmailAlreadyExistsError(AppException):
    pass


class UsernameAlreadyExistsError(AppException):
    pass


class InvalidCredentialsError(AppException):
    pass


class UserNotFoundError(AppException):
    pass


class ProjectNotFoundError(AppException):
    pass


class TaskNotFoundError(AppException):
    pass


class PermissionDeniedError(AppException):
    pass