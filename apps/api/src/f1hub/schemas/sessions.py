"""
F1 Intelligence Hub - Session Schemas

Schemas for F1 sessions (FP1, FP2, FP3, Q, Sprint, Race).
"""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .common import TimestampMixin


class SessionBase(BaseModel):
    """Base session schema."""

    event_id: UUID = Field(description="Event UUID")
    session_type: str = Field(description="Session type (FP1, FP2, FP3, Q, Sprint, Race)")
    session_date: date = Field(description="Session date")


class SessionResponse(SessionBase, TimestampMixin):
    """Session response schema."""

    id: UUID = Field(description="Session UUID")
    is_ingested: bool = Field(description="Whether data has been ingested")
    source: Optional[str] = Field(default=None, description="Data source (fastf1, openf1, jolpica)")
    lap_count: Optional[int] = Field(default=None, description="Number of laps")
    stint_count: Optional[int] = Field(default=None, description="Number of stints")

    model_config = ConfigDict(from_attributes=True)


class SessionListResponse(BaseModel):
    """List of sessions response."""

    total: int = Field(description="Total number of sessions")
    sessions: list[SessionResponse] = Field(description="List of sessions")

    model_config = ConfigDict(from_attributes=True)
