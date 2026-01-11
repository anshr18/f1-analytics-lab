"""
F1 Intelligence Hub - Race Schemas

Schemas for seasons and events (race weekends).
"""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .common import TimestampMixin


class SeasonResponse(BaseModel):
    """Season response schema."""

    year: int = Field(description="Season year")
    event_count: Optional[int] = Field(default=None, description="Number of events in season")

    model_config = ConfigDict(from_attributes=True)


class EventBase(BaseModel):
    """Base event schema."""

    season_year: int = Field(description="Season year")
    round_number: int = Field(description="Round number in season")
    event_name: str = Field(description="Event name (e.g., 'Bahrain Grand Prix')")
    country: str = Field(description="Country")
    location: str = Field(description="Location/Circuit name")
    event_date: date = Field(description="Date of the race")


class EventResponse(EventBase, TimestampMixin):
    """Event response schema."""

    id: UUID = Field(description="Event UUID")
    session_count: Optional[int] = Field(default=None, description="Number of sessions")

    model_config = ConfigDict(from_attributes=True)


class EventListResponse(BaseModel):
    """List of events response."""

    total: int = Field(description="Total number of events")
    events: list[EventResponse] = Field(description="List of events")

    model_config = ConfigDict(from_attributes=True)
