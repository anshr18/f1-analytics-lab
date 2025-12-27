"""
F1 Intelligence Hub - API Router

Aggregates all API v1 routers.
"""

from fastapi import APIRouter

from .v1 import drivers, health, ingest, laps, races, sessions, stints

# Create main API router
api_router = APIRouter()

# Include all v1 routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(races.router, prefix="/races", tags=["Races"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(laps.router, prefix="/laps", tags=["Laps"])
api_router.include_router(stints.router, prefix="/stints", tags=["Stints"])
api_router.include_router(drivers.router, prefix="/drivers", tags=["Drivers"])
api_router.include_router(ingest.router, tags=["Ingest"])
