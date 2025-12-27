"""
F1 Intelligence Hub - Pydantic Schemas

Request/Response schemas for API endpoints.
"""

from .common import ErrorResponse, HealthResponse, PaginationParams, TimestampMixin
from .drivers import DriverListResponse, DriverResponse
from .ingest import IngestSessionRequest, IngestSessionResponse, TaskStatusResponse
from .laps import LapListResponse, LapResponse
from .races import EventListResponse, EventResponse, SeasonResponse
from .sessions import SessionListResponse, SessionResponse
from .stints import StintListResponse, StintResponse

__all__ = [
    # Common
    "TimestampMixin",
    "PaginationParams",
    "HealthResponse",
    "ErrorResponse",
    # Races
    "SeasonResponse",
    "EventResponse",
    "EventListResponse",
    # Sessions
    "SessionResponse",
    "SessionListResponse",
    # Laps
    "LapResponse",
    "LapListResponse",
    # Stints
    "StintResponse",
    "StintListResponse",
    # Drivers
    "DriverResponse",
    "DriverListResponse",
    # Ingest
    "IngestSessionRequest",
    "IngestSessionResponse",
    "TaskStatusResponse",
]
