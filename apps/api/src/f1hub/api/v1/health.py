"""
F1 Intelligence Hub - Health Check Endpoint

Enhanced health check with database and Redis status.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from ...core.config import get_settings
from ...core.dependencies import get_db
from ...schemas.common import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check API health status including database and Redis connectivity",
)
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.

    Returns application status and checks external dependencies.
    """
    settings = get_settings()

    # Check database connectivity
    db_status = {"status": "unknown"}
    try:
        db.execute(text("SELECT 1"))
        db_status = {"status": "healthy", "connected": True}
    except Exception as e:
        db_status = {"status": "unhealthy", "connected": False, "error": str(e)}

    # TODO: Check Redis connectivity in Week 3
    redis_status = {"status": "not_checked"}

    return HealthResponse(
        status="healthy" if db_status["status"] == "healthy" else "degraded",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        database=db_status,
        redis=redis_status,
    )
