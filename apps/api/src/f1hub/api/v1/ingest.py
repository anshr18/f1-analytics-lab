"""
F1 Intelligence Hub - Ingest API

Endpoints for data ingestion (placeholder for Week 3).
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...core.dependencies import get_db
from ...schemas.ingest import IngestSessionRequest, IngestSessionResponse, TaskStatusResponse

router = APIRouter()


@router.post(
    "/ingest/session",
    response_model=IngestSessionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest Session Data",
    description="Trigger ingestion of session data from FastF1/OpenF1/Jolpica (Week 3)",
)
async def ingest_session(request: IngestSessionRequest, db: Session = Depends(get_db)):
    """
    Ingest session data.

    This endpoint will be fully implemented in Week 3 with Celery workers.

    Args:
        request: Ingestion request parameters
        db: Database session

    Returns:
        Task ID for tracking ingestion progress
    """
    # TODO: Week 3 - Implement Celery task for ingestion
    return IngestSessionResponse(
        task_id="placeholder-task-id",
        status="pending",
        message="Ingestion endpoint will be implemented in Week 3",
    )


@router.get(
    "/ingest/status/{task_id}",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Ingestion Status",
    description="Check status of an ingestion task (Week 3)",
)
async def get_task_status(task_id: str):
    """
    Get task status.

    This endpoint will be fully implemented in Week 3 with Celery task tracking.

    Args:
        task_id: Celery task ID

    Returns:
        Task status and progress
    """
    # TODO: Week 3 - Implement Celery task status checking
    return TaskStatusResponse(
        task_id=task_id,
        status="PENDING",
        progress=None,
        current="Waiting for Week 3 implementation",
        result=None,
        error=None,
        session_id=None,
    )
