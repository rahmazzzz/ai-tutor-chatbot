class AppError(Exception):
    """Base class for all application-specific errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class NotFoundError(AppError):
    """Resource not found."""
    pass

class ValidationError(AppError):
    """Validation failed."""
    pass

class AuthError(AppError):
    """Authentication or authorization failed."""
    pass

class ExternalServiceError(AppError):
    """Error from external APIs or services."""
    pass
