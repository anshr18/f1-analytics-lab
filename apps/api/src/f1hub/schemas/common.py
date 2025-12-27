"""
F1 Intelligence Hub - Common Schemas

Common Pydantic schemas used across all endpoints.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at timestamps."""

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginationParams(BaseModel):
    """Query parameters for pagination."""

    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, le=1000, ge=1, description="Maximum number of records to return")


class PaginatedResponse(BaseModel):
    """Base paginated response."""

    total: int = Field(description="Total number of records")
    skip: int = Field(description="Number of records skipped")
    limit: int = Field(description="Maximum number of records returned")
    items: list[Any] = Field(description="List of items")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(description="Health status")
    app: str = Field(description="Application name")
    version: str = Field(description="Application version")
    environment: str = Field(description="Environment name")
    database: Optional[Dict[str, Any]] = Field(default=None, description="Database status")
    redis: Optional[Dict[str, Any]] = Field(default=None, description="Redis status")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    detail: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
