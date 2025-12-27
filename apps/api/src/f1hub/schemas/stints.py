"""
F1 Intelligence Hub - Stint Schemas

Schemas for tyre stint data.
"""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .common import TimestampMixin


class StintBase(BaseModel):
    """Base stint schema."""

    session_id: UUID = Field(description="Session UUID")
    driver_id: str = Field(description="Driver ID")
    stint_number: int = Field(description="Stint number")
    compound: str = Field(description="Tyre compound")


class StintResponse(StintBase, TimestampMixin):
    """Stint response schema."""

    id: UUID = Field(description="Stint UUID")
    lap_start: int = Field(description="First lap of stint")
    lap_end: Optional[int] = Field(default=None, description="Last lap of stint")
    total_laps: Optional[int] = Field(default=None, description="Total laps in stint")

    model_config = ConfigDict(from_attributes=True)


class StintListResponse(BaseModel):
    """List of stints response."""

    total: int = Field(description="Total number of stints")
    stints: list[StintResponse] = Field(description="List of stints")

    model_config = ConfigDict(from_attributes=True)
