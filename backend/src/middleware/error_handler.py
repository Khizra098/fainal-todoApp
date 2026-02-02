"""
Error handling middleware for the verification system.
This module provides centralized error handling for the application.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Union
from pydantic import ValidationError
import logging
from ..utils.logging import get_logger


logger = get_logger(__name__)


class BusinessLogicError(Exception):
    """
    Custom exception for business logic errors
    """
    def __init__(self, message: str, error_code: str = "BUSINESS_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(Exception):
    """
    Custom exception for validation errors
    """
    def __init__(self, message: str, field: str = None, error_code: str = "VALIDATION_ERROR"):
        self.message = message
        self.field = field
        self.error_code = error_code
        super().__init__(self.message)


class NotFoundError(Exception):
    """
    Custom exception for not found errors
    """
    def __init__(self, resource: str, identifier: str = None, error_code: str = "NOT_FOUND"):
        self.resource = resource
        self.identifier = identifier
        self.error_code = error_code
        if identifier:
            message = f"{resource} with identifier '{identifier}' not found"
        else:
            message = f"{resource} not found"
        self.message = message
        super().__init__(self.message)


class UnauthorizedError(Exception):
    """
    Custom exception for unauthorized access
    """
    def __init__(self, message: str = "Unauthorized access", error_code: str = "UNAUTHORIZED"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ForbiddenError(Exception):
    """
    Custom exception for forbidden access
    """
    def __init__(self, message: str = "Forbidden access", error_code: str = "FORBIDDEN"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for the application
    """
    logger.error(f"Unhandled exception occurred: {exc}", exc_info=True)

    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": "HTTP_ERROR",
                    "message": exc.detail,
                    "details": {}
                }
            }
        )
    elif isinstance(exc, BusinessLogicError):
        logger.warning(f"Business logic error: {exc.message}")
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": {}
                }
            }
        )
    elif isinstance(exc, ValidationError):
        logger.warning(f"Validation error: {exc.message}")
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": {"field": exc.field} if exc.field else {}
                }
            }
        )
    elif isinstance(exc, NotFoundError):
        logger.info(f"Not found error: {exc.message}")
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": {
                        "resource": exc.resource,
                        "identifier": exc.identifier
                    } if exc.identifier else {"resource": exc.resource}
                }
            }
        )
    elif isinstance(exc, UnauthorizedError):
        logger.warning(f"Unauthorized error: {exc.message}")
        return JSONResponse(
            status_code=401,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": {}
                }
            }
        )
    elif isinstance(exc, ForbiddenError):
        logger.warning(f"Forbidden error: {exc.message}")
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.message,
                    "details": {}
                }
            }
        )
    elif isinstance(exc, ValueError):
        logger.warning(f"Value error: {str(exc)}")
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "VALUE_ERROR",
                    "message": str(exc),
                    "details": {}
                }
            }
        )
    else:
        logger.error(f"Unexpected error occurred: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal server error occurred",
                    "details": {}
                }
            }
        )


def add_exception_handlers(app):
    """
    Add exception handlers to the FastAPI application
    """
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(HTTPException, global_exception_handler)
    app.add_exception_handler(BusinessLogicError, global_exception_handler)
    app.add_exception_handler(ValidationError, global_exception_handler)
    app.add_exception_handler(NotFoundError, global_exception_handler)
    app.add_exception_handler(UnauthorizedError, global_exception_handler)
    app.add_exception_handler(ForbiddenError, global_exception_handler)