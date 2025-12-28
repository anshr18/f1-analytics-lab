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
    LapTimePredictionResponse,
    OvertakePredictionResponse,
    PredictionRequest,
    TyreDegradationPredictionResponse,
)
from f1hub.services.ml_service import MLService

router = APIRouter(prefix="/predictions")


@router.get("/tyre-degradation/{stint_id}", response_model=TyreDegradationPredictionResponse)
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


@router.get("/lap-time", response_model=LapTimePredictionResponse)
async def predict_lap_time(
    tyre_age: int,
    compound: str,
    track_status: str,
    position: int,
    driver_id: str,
    db: Session = Depends(get_db),
    minio: Minio = Depends(get_minio_client),
) -> LapTimePredictionResponse:
    """Predict lap time for given conditions.

    Args:
        tyre_age: Laps on current tyre
        compound: Tyre compound (SOFT, MEDIUM, HARD)
        track_status: Track status (GREEN, YELLOW, SC, VSC, RED)
        position: Current position
        driver_id: Driver identifier
        db: Database session
        minio: MinIO client

    Returns:
        Prediction with lap time in seconds

    Raises:
        HTTPException: If model not available
    """
    try:
        ml_service = MLService(db, minio)
        result = ml_service.predict_lap_time(
            tyre_age, compound, track_status, position, driver_id
        )

        return LapTimePredictionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/overtake", response_model=OvertakePredictionResponse)
async def predict_overtake(
    gap_seconds: float,
    closing_rate: float,
    tyre_advantage: int,
    drs_available: bool,
    lap_number: int,
    db: Session = Depends(get_db),
    minio: Minio = Depends(get_minio_client),
) -> OvertakePredictionResponse:
    """Predict overtake probability.

    Args:
        gap_seconds: Time gap between cars (seconds)
        closing_rate: Gap change per lap (s/lap, negative = closing)
        tyre_advantage: Compound advantage (-2 to +2)
        drs_available: Whether DRS is available
        lap_number: Current lap number
        db: Database session
        minio: MinIO client

    Returns:
        Prediction with overtake probability (0-1)

    Raises:
        HTTPException: If model not available
    """
    try:
        ml_service = MLService(db, minio)
        result = ml_service.predict_overtake(
            gap_seconds, closing_rate, tyre_advantage, drs_available, lap_number
        )

        return OvertakePredictionResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
