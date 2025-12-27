"""
F1 Intelligence Hub - Custom Exceptions

Application-specific exceptions and error handlers for FastAPI.
"""

from typing import Any, Dict

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class F1HubException(Exception):
    """Base exception for all F1 Intelligence Hub errors."""

    def __init__(self, message: str, details: Dict[str, Any] | None = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DataIngestionError(F1HubException):
    """Raised when data ingestion fails."""

    pass


class DataNotFoundError(F1HubException):
    """Raised when requested data is not found."""

    pass


class DatabaseError(F1HubException):
    """Raised when database operations fail."""

    pass


class ValidationError(F1HubException):
    """Raised when data validation fails."""

    pass


class ExternalAPIError(F1HubException):
    """Raised when external API calls fail."""

    pass


class CeleryTaskError(F1HubException):
    """Raised when Celery task execution fails."""

    pass


# ============================================================================
# FastAPI Exception Handlers
# ============================================================================


async def f1hub_exception_handler(request: Request, exc: F1HubException) -> JSONResponse:
    """
    Handle F1Hub custom exceptions.

    Args:
        request: FastAPI request
        exc: F1HubException instance

    Returns:
        JSONResponse: Formatted error response
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def data_not_found_handler(request: Request, exc: DataNotFoundError) -> JSONResponse:
    """
    Handle DataNotFoundError with 404 status.

    Args:
        request: FastAPI request
        exc: DataNotFoundError instance

    Returns:
        JSONResponse: 404 error response
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "DataNotFound",
            "message": exc.message,
            "details": exc.details,
        },
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handle ValidationError with 422 status.

    Args:
        request: FastAPI request
        exc: ValidationError instance

    Returns:
        JSONResponse: 422 error response
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": exc.message,
            "details": exc.details,
        },
    )


async def external_api_error_handler(request: Request, exc: ExternalAPIError) -> JSONResponse:
    """
    Handle ExternalAPIError with 502 status.

    Args:
        request: FastAPI request
        exc: ExternalAPIError instance

    Returns:
        JSONResponse: 502 error response
    """
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={
            "error": "ExternalAPIError",
            "message": exc.message,
            "details": exc.details,
        },
    )
