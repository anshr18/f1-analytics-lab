"""
Model Registry Schemas

Pydantic models for ML model registry requests and responses.
"""

from datetime import datetime
from typing import Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ModelResponse(BaseModel):
    """Model registry entry response."""

    id: UUID
    model_name: str
    version: str
    model_type: str
    status: str
    metrics: Dict
    artifact_path: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelListResponse(BaseModel):
    """List of models response."""

    models: list[ModelResponse]
    total: int


class ModelTrainingRequest(BaseModel):
    """Request to train a model."""

    model_name: str = Field(..., description="Name of the model to train")
    parameters: Optional[Dict] = Field(
        default=None, description="Optional training parameters"
    )


class ModelTrainingResponse(BaseModel):
    """Response from model training trigger."""

    task_id: str
    model_name: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """Response for training task status."""

    task_id: str
    status: str
    result: Optional[Dict] = None
    error: Optional[str] = None
    progress: Optional[str] = None
