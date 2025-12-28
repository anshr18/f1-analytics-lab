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


class LapTimePredictionResponse(BaseModel):
    """Response from lap time prediction."""

    predicted_lap_time: float
    tyre_age: int
    compound: str
    track_status: str
    position: int
    driver_id: str
    model_version: str


class OvertakePredictionResponse(BaseModel):
    """Response from overtake probability prediction."""

    overtake_probability: float
    gap_seconds: float
    closing_rate: float
    tyre_advantage: int
    drs_available: bool
    lap_number: int
    model_version: str


class RaceResultPredictionResponse(BaseModel):
    """Response from race result prediction."""

    predicted_position: int
    top3_probabilities: Dict[int, float]
    grid_position: int
    avg_lap_time: float
    driver_id: str
    model_version: str


class PredictionResponse(BaseModel):
    """Generic prediction response."""

    prediction_id: UUID | None = None
    model_name: str
    version: str
    prediction_value: Any
    confidence: Dict[str, float] | None = None
