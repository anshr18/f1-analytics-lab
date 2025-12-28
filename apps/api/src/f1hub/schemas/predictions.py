"""
Prediction Schemas

Pydantic models for ML prediction requests and responses.
"""

from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Request to create a prediction."""

    model_name: str = Field(..., description="Name of the model to use")
    version: str = Field(default="latest", description="Model version")
    input_data: Dict[str, Any] = Field(..., description="Input features for prediction")


class TyreDegradationPredictionResponse(BaseModel):
    """Response from tyre degradation prediction."""

    stint_id: str
    predicted_deg_per_lap: float
    compound: str
    driver_id: str
    model_version: str


class PredictionResponse(BaseModel):
    """Generic prediction response."""

    prediction_id: UUID | None = None
    model_name: str
    version: str
    prediction_value: Any
    confidence: Dict[str, float] | None = None
