"""
F1 Intelligence Hub - Stints API

Endpoints for tyre stint data.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ...core.dependencies import get_db
from ...core.errors import DataNotFoundError
from ...db.models.timing import Stint
from ...schemas.stints import StintListResponse, StintResponse

router = APIRouter()


@router.get(
    "/stints",
    response_model=StintListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Stints",
    description="Get stint data with filtering",
)
async def list_stints(
    session_id: UUID = Query(..., description="Session UUID (required)"),
    driver_id: str = Query(None, description="Filter by driver ID"),
    db: Session = Depends(get_db),
):
    """
    List stints for a session.

    Args:
        session_id: Session UUID (required)
        driver_id: Optional driver ID filter
        db: Database session

    Returns:
        List of stints
    """
    query = db.query(Stint).filter(Stint.session_id == session_id)

    if driver_id:
        query = query.filter(Stint.driver_id == driver_id)

    # Order by driver and stint number
    query = query.order_by(Stint.driver_id, Stint.stint_number)

    stints = query.all()
    total = len(stints)

    return StintListResponse(
        total=total,
        stints=[StintResponse.model_validate(stint) for stint in stints],
    )


@router.get(
    "/stints/{stint_id}",
    response_model=StintResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Stint",
    description="Get details for a specific stint",
)
async def get_stint(stint_id: UUID, db: Session = Depends(get_db)):
    """
    Get stint by ID.

    Args:
        stint_id: Stint UUID
        db: Database session

    Returns:
        Stint details

    Raises:
        404: Stint not found
    """
    stint = db.query(Stint).filter(Stint.id == stint_id).first()

    if not stint:
        raise DataNotFoundError(f"Stint {stint_id} not found")

    return StintResponse.model_validate(stint)
