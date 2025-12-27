"""
F1 Intelligence Hub - Driver Schemas

Schemas for driver information.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .common import TimestampMixin


class DriverBase(BaseModel):
    """Base driver schema."""

    driver_id: str = Field(description="Driver ID (e.g., 'max_verstappen')")
    full_name: str = Field(description="Full name")
    abbreviation: str = Field(description="3-letter abbreviation (e.g., 'VER')")
    number: Optional[int] = Field(default=None, description="Permanent race number")
    country: Optional[str] = Field(default=None, description="ISO 3166-1 alpha-3 country code")


class DriverResponse(DriverBase, TimestampMixin):
    """Driver response schema."""

    model_config = ConfigDict(from_attributes=True)


class DriverListResponse(BaseModel):
    """List of drivers response."""

    total: int = Field(description="Total number of drivers")
    drivers: list[DriverResponse] = Field(description="List of drivers")

    model_config = ConfigDict(from_attributes=True)
