"""
Feature Schemas

Pydantic models for feature computation requests and responses.
"""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FeatureStatusResponse(BaseModel):
    """Feature status for a session."""

    session_id: UUID
    has_features: bool
    lap_features: int
    stint_features: int
    battle_features: int

    class Config:
        from_attributes = True


class FeatureComputeResponse(BaseModel):
    """Feature computation result."""

    session_id: UUID
    lap_features_count: int
    stint_features_count: int
    battle_features_count: int
    duration_seconds: float
    errors: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True
