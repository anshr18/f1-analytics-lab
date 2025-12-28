"""
F1 Intelligence Hub - API Router

Aggregates all API v1 routers.
"""

from fastapi import APIRouter

from .v1 import drivers, features, health, ingest, laps, models, races, sessions, stints

# Create main API router
api_router = APIRouter()

# Include all v1 routers
# Note: Routers define their own paths (e.g., /sessions, /seasons, /laps)
# We don't add prefixes here to keep URLs clean
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(races.router, tags=["Races"])
api_router.include_router(sessions.router, tags=["Sessions"])
api_router.include_router(laps.router, tags=["Laps"])
api_router.include_router(stints.router, tags=["Stints"])
api_router.include_router(drivers.router, tags=["Drivers"])
api_router.include_router(ingest.router, tags=["Ingest"])
api_router.include_router(features.router, tags=["Features"])
api_router.include_router(models.router, tags=["Models"])
