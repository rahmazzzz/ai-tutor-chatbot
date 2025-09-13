# app/exceptions/decorators.py
from functools import wraps
from fastapi.responses import JSONResponse
from .http_exceptions import to_http_exception
import asyncio

def handle_exceptions(func):
    """
    Decorator to wrap async service or route functions and convert AppErrors
    into HTTP responses.
    """
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                http_exc = to_http_exception(e)
                return JSONResponse(
                    status_code=http_exc.status_code,
                    content={"detail": http_exc.detail}
                )
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                http_exc = to_http_exception(e)
                return JSONResponse(
                    status_code=http_exc.status_code,
                    content={"detail": http_exc.detail}
                )
        return sync_wrapper
