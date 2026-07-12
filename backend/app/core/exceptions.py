"""
Custom exception hierarchy. Services raise these; the global error
middleware (middleware/error_handler.py) converts them into consistent
JSON responses. This decouples business logic from HTTP status codes.
"""


class AppException(Exception):
    status_code: int = 500
    detail: str = "An unexpected error occurred"

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class InvalidCredentialsException(AppException):
    status_code = 401
    detail = "Invalid email or password"


class TokenExpiredException(AppException):
    status_code = 401
    detail = "Token has expired"


class InvalidTokenException(AppException):
    status_code = 401
    detail = "Invalid or malformed token"


class InactiveUserException(AppException):
    status_code = 403
    detail = "This account has been deactivated"


class InsufficientPermissionsException(AppException):
    status_code = 403
    detail = "You do not have permission to perform this action"


class DuplicateResourceException(AppException):
    status_code = 409
    detail = "Resource already exists"


class ResourceNotFoundException(AppException):
    status_code = 404
    detail = "Resource not found"