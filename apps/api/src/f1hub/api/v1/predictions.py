"""
Prediction API Endpoints

Endpoints for making ML model predictions.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from minio import Minio
from sqlalchemy.orm import Session

from f1hub.core.dependencies import get_db, get_minio_client
from f1hub.schemas.predictions import (
    PredictionRequest,
    TyreDegradationPredictionResponse,
)
from f1hub.services.ml_service import MLService

router = APIRouter(prefix="/predictions")


@router.post("/tyre-degradation/{stint_id}", response_model=TyreDegradationPredictionResponse)
async def predict_tyre_degradation(
    stint_id: UUID,
    db: Session = Depends(get_db),
    minio: Minio = Depends(get_minio_client),
) -> TyreDegradationPredictionResponse:
    """Predict tyre degradation for a stint.

    Args:
        stint_id: Stint UUID
        db: Database session
        minio: MinIO client

    Returns:
        Prediction with deg_per_lap value

    Raises:
        HTTPException: If stint not found or model not available
    """
    try:
        ml_service = MLService(db, minio)
        result = ml_service.predict_tyre_degradation(stint_id)

        return TyreDegradationPredictionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
