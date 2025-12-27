"""
F1 Intelligence Hub - Ingest Schemas

Schemas for data ingestion endpoints.
"""

from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class IngestSessionRequest(BaseModel):
    """Request to ingest session data."""

    year: int = Field(description="Season year", ge=2018, le=2030)
    round_number: int = Field(description="Round number", ge=1, le=24)
    session_type: str = Field(description="Session type (FP1, FP2, FP3, Q, Sprint, Race)")
    source: str = Field(default="fastf1", description="Data source (fastf1, openf1, jolpica)")


class IngestSessionResponse(BaseModel):
    """Response from session ingestion request."""

    task_id: str = Field(description="Celery task ID for tracking")
    status: str = Field(description="Task status (pending, started, success, failure)")
    message: str = Field(description="Status message")


class TaskStatusResponse(BaseModel):
    """Task status response."""

    task_id: str = Field(description="Celery task ID")
    status: str = Field(description="Task status (PENDING, STARTED, SUCCESS, FAILURE)")
    progress: Optional[int] = Field(default=None, description="Progress percentage (0-100)")
    current: Optional[str] = Field(default=None, description="Current operation")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Task result (when completed)")
    error: Optional[str] = Field(default=None, description="Error message (if failed)")
    session_id: Optional[UUID] = Field(default=None, description="Session UUID (when completed)")
