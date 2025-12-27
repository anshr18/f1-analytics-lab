"""
F1 Intelligence Hub - Races API

Endpoints for seasons and events (race weekends).
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...core.dependencies import get_db
from ...core.errors import DataNotFoundError
from ...db.models.core import Event, Season
from ...schemas.races import EventListResponse, EventResponse, SeasonResponse

router = APIRouter()


@router.get(
    "/seasons",
    response_model=List[SeasonResponse],
    status_code=status.HTTP_200_OK,
    summary="List Seasons",
    description="Get list of all available F1 seasons",
)
async def list_seasons(db: Session = Depends(get_db)):
    """
    List all available seasons.

    Returns seasons ordered by year (descending).
    """
    seasons = (
        db.query(Season, func.count(Event.id).label("event_count"))
        .outerjoin(Event, Season.year == Event.season_year)
        .group_by(Season.year)
        .order_by(Season.year.desc())
        .all()
    )

    return [
        SeasonResponse(year=season.year, event_count=event_count)
        for season, event_count in seasons
    ]


@router.get(
    "/events",
    response_model=EventListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Events",
    description="Get list of events with optional filtering by season",
)
async def list_events(
    season_year: int = Query(None, description="Filter by season year"),
    db: Session = Depends(get_db),
):
    """
    List events with optional season filter.

    Args:
        season_year: Optional season year filter
        db: Database session

    Returns:
        List of events
    """
    query = db.query(Event)

    if season_year:
        query = query.filter(Event.season_year == season_year)

    events = query.order_by(Event.season_year.desc(), Event.round_number).all()
    total = len(events)

    return EventListResponse(
        total=total,
        events=[EventResponse.model_validate(event) for event in events],
    )


@router.get(
    "/events/{event_id}",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Event",
    description="Get details for a specific event",
)
async def get_event(event_id: UUID, db: Session = Depends(get_db)):
    """
    Get event by ID.

    Args:
        event_id: Event UUID
        db: Database session

    Returns:
        Event details

    Raises:
        404: Event not found
    """
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise DataNotFoundError(f"Event {event_id} not found")

    return EventResponse.model_validate(event)
