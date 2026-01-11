"""
F1 Intelligence Hub - Features API

Endpoints for computing and querying ML features.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from f1hub.core.dependencies import get_db
from f1hub.db.models.features import BattleFeature, LapFeature, StintFeature
from f1hub.db.models.timing import Lap, Stint
from f1hub.schemas.features import FeatureComputeResponse, FeatureStatusResponse
from f1hub.services.feature_builder import FeatureBuilderService

router = APIRouter()


@router.post(
    "/features/compute/{session_id}",
    response_model=FeatureComputeResponse,
    status_code=status.HTTP_200_OK,
    summary="Compute Features",
    description="Compute lap, stint, and battle features for a session",
)
async def compute_features(
    session_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Compute all ML features for a session.

    This endpoint will:
    1. Compute lap-level features (time deltas, tyre age, encodings)
    2. Compute stint-level features (degradation via linear regression)
    3. Compute battle features (overtake detection, gaps, closing rates)

    Args:
        session_id: Session UUID
        db: Database session

    Returns:
        Feature computation summary with counts and duration

    Raises:
        500: If feature computation fails
    """
    try:
        service = FeatureBuilderService(db)
        result = service.build_features_for_session(session_id)

        return FeatureComputeResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feature computation failed: {str(e)}",
        )


@router.get(
    "/features/status/{session_id}",
    response_model=FeatureStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Feature Status",
    description="Check if features exist for a session",
)
async def get_feature_status(
    session_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Check if features have been computed for a session.

    Args:
        session_id: Session UUID
        db: Database session

    Returns:
        Feature status with counts for each feature type
    """
    # Count lap features
    lap_count = (
        db.query(LapFeature)
        .join(Lap)
        .filter(Lap.session_id == session_id)
        .count()
    )

    # Count stint features
    stint_count = (
        db.query(StintFeature)
        .join(Stint)
        .filter(Stint.session_id == session_id)
        .count()
    )

    # Count battle features
    battle_count = (
        db.query(BattleFeature)
        .filter(BattleFeature.session_id == session_id)
        .count()
    )

    return FeatureStatusResponse(
        session_id=session_id,
        has_features=lap_count > 0,
        lap_features=lap_count,
        stint_features=stint_count,
        battle_features=battle_count,
    )
