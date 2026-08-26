from fastapi import HTTPException, status


class AppException(HTTPException):
    """Base application exception."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class ForbiddenError(AppException):
    def __init__(self, detail: str = "You do not have permission to access this resource"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class UnauthorizedError(AppException):
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class ConflictError(AppException):
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class ValidationError(AppException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class TenantIsolationError(ForbiddenError):
    def __init__(self, detail: str = "Tenant isolation violation"):
        super().__init__(detail=detail)


class AIRuntimeError(AppException):
    def __init__(self, detail: str = "AI service error"):
        super().__init__(detail=detail, status_code=status.HTTP_502_BAD_GATEWAY)


class CodeExecutionError(AppException):
    def __init__(self, detail: str = "Code execution failed"):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
