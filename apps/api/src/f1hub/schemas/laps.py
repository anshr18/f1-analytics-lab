"""
F1 Intelligence Hub - Lap Schemas

Schemas for lap timing data.
"""

from datetime import timedelta
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .common import TimestampMixin


class LapBase(BaseModel):
    """Base lap schema."""

    session_id: UUID = Field(description="Session UUID")
    driver_id: str = Field(description="Driver ID")
    lap_number: int = Field(description="Lap number")


class LapResponse(LapBase, TimestampMixin):
    """Lap response schema."""

    id: UUID = Field(description="Lap UUID")
    lap_time: Optional[timedelta] = Field(default=None, description="Total lap time")
    sector_1_time: Optional[timedelta] = Field(default=None, description="Sector 1 time")
    sector_2_time: Optional[timedelta] = Field(default=None, description="Sector 2 time")
    sector_3_time: Optional[timedelta] = Field(default=None, description="Sector 3 time")
    compound: Optional[str] = Field(default=None, description="Tyre compound")
    tyre_life: Optional[int] = Field(default=None, description="Tyre life in laps")
    stint_id: Optional[UUID] = Field(default=None, description="Stint UUID")
    track_status: Optional[str] = Field(default=None, description="Track status")
    is_personal_best: Optional[bool] = Field(default=False, description="Personal best lap")
    position: Optional[int] = Field(default=None, description="Position at end of lap")
    deleted: Optional[bool] = Field(default=False, description="Lap deleted")
    is_pit_out_lap: Optional[bool] = Field(default=False, description="Pit out lap")
    is_pit_in_lap: Optional[bool] = Field(default=False, description="Pit in lap")
    telemetry: Optional[Dict[str, Any]] = Field(default=None, description="Additional telemetry")

    model_config = ConfigDict(from_attributes=True)


class LapListResponse(BaseModel):
    """List of laps response."""

    total: int = Field(description="Total number of laps")
    laps: list[LapResponse] = Field(description="List of laps")

    model_config = ConfigDict(from_attributes=True)
