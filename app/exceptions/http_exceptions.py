# app/exceptions/http_exceptions.py
from fastapi import HTTPException, status
from app.exceptions.base_exceptions import NotFoundError, ValidationError, AuthError, ExternalServiceError
from json.decoder import JSONDecodeError

def to_http_exception(error: Exception) -> HTTPException:
    """
    Convert any exception into a proper FastAPI HTTPException.
    Handles custom exceptions, JSONDecodeError, and falls back to 500.
    """
    if isinstance(error, HTTPException):
        return error
    if isinstance(error, NotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)
    if isinstance(error, ValidationError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error.message)
    if isinstance(error, AuthError):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error.message)
    if isinstance(error, ExternalServiceError):
        return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=error.message)
    if isinstance(error, JSONDecodeError):
        return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Invalid JSON response")
    # fallback for all other exceptions
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(error))
