"""
F1 Intelligence Hub - Laps API

Endpoints for lap timing data.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ...core.dependencies import get_db
from ...core.errors import DataNotFoundError
from ...db.models.timing import Lap
from ...schemas.laps import LapListResponse, LapResponse

router = APIRouter()


@router.get(
    "/laps",
    response_model=LapListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Laps",
    description="Get lap timing data with filtering",
)
async def list_laps(
    session_id: UUID = Query(..., description="Session UUID (required)"),
    driver_id: str = Query(None, description="Filter by driver ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
):
    """
    List laps for a session.

    Args:
        session_id: Session UUID (required)
        driver_id: Optional driver ID filter
        skip: Pagination offset
        limit: Pagination limit
        db: Database session

    Returns:
        List of laps
    """
    query = db.query(Lap).filter(Lap.session_id == session_id)

    if driver_id:
        query = query.filter(Lap.driver_id == driver_id)

    # Order by lap number
    query = query.order_by(Lap.lap_number)

    total = query.count()
    laps = query.offset(skip).limit(limit).all()

    return LapListResponse(
        total=total,
        laps=[LapResponse.model_validate(lap) for lap in laps],
    )


@router.get(
    "/laps/{lap_id}",
    response_model=LapResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Lap",
    description="Get details for a specific lap",
)
async def get_lap(lap_id: UUID, db: Session = Depends(get_db)):
    """
    Get lap by ID.

    Args:
        lap_id: Lap UUID
        db: Database session

    Returns:
        Lap details

    Raises:
        404: Lap not found
    """
    lap = db.query(Lap).filter(Lap.id == lap_id).first()

    if not lap:
        raise DataNotFoundError(f"Lap {lap_id} not found")

    return LapResponse.model_validate(lap)
