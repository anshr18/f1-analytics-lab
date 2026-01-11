"""
F1 Intelligence Hub - Drivers API

Endpoints for driver information.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...core.dependencies import get_db
from ...core.errors import DataNotFoundError
from ...db.models.core import Driver
from ...schemas.drivers import DriverListResponse, DriverResponse

router = APIRouter()


@router.get(
    "/drivers",
    response_model=DriverListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Drivers",
    description="Get list of all drivers",
)
async def list_drivers(db: Session = Depends(get_db)):
    """
    List all drivers.

    Returns drivers ordered by full name.
    """
    drivers = db.query(Driver).order_by(Driver.full_name).all()
    total = len(drivers)

    return DriverListResponse(
        total=total,
        drivers=[DriverResponse.model_validate(driver) for driver in drivers],
    )


@router.get(
    "/drivers/{driver_id}",
    response_model=DriverResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Driver",
    description="Get details for a specific driver",
)
async def get_driver(driver_id: str, db: Session = Depends(get_db)):
    """
    Get driver by ID.

    Args:
        driver_id: Driver ID (e.g., 'max_verstappen')
        db: Database session

    Returns:
        Driver details

    Raises:
        404: Driver not found
    """
    driver = db.query(Driver).filter(Driver.driver_id == driver_id).first()

    if not driver:
        raise DataNotFoundError(f"Driver {driver_id} not found")

    return DriverResponse.model_validate(driver)
