"""
F1 Intelligence Hub - Ingest API

Endpoints for data ingestion via Celery tasks.
"""

from uuid import UUID

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.dependencies import get_db
from ...schemas.ingest import IngestSessionRequest, IngestSessionResponse, TaskStatusResponse
from ...workers.celery_app import celery_app
from ...workers.tasks.ingest import ingest_session_task

router = APIRouter()


@router.post(
    "/ingest/session",
    response_model=IngestSessionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Ingest Session Data",
    description="Trigger asynchronous ingestion of session data from FastF1/OpenF1/Jolpica",
)
async def ingest_session(request: IngestSessionRequest, db: Session = Depends(get_db)):
    """
    Ingest session data asynchronously.

    Triggers a Celery task to load data from the specified source.

    Args:
        request: Ingestion request parameters
        db: Database session

    Returns:
        Task ID for tracking ingestion progress
    """
    # Dispatch Celery task
    task = ingest_session_task.delay(
        year=request.year,
        round_number=request.round_number,
        session_type=request.session_type,
        source=request.source,
    )

    return IngestSessionResponse(
        task_id=task.id,
        status="pending",
        message=f"Ingestion task started for {request.year} Round {request.round_number} {request.session_type}",
    )


@router.get(
    "/ingest/status/{task_id}",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Ingestion Status",
    description="Check status of an ingestion task",
)
async def get_task_status(task_id: str):
    """
    Get task status.

    Retrieves the current status and progress of a Celery ingestion task.

    Args:
        task_id: Celery task ID

    Returns:
        Task status and progress
    """
    task = AsyncResult(task_id, app=celery_app)

    if task.state == "PENDING":
        response = TaskStatusResponse(
            task_id=task_id,
            status="PENDING",
            progress=0,
            current="Task is waiting to be processed",
        )
    elif task.state == "PROGRESS":
        response = TaskStatusResponse(
            task_id=task_id,
            status="PROGRESS",
            progress=task.info.get("progress", 0),
            current=task.info.get("current", "Processing"),
        )
    elif task.state == "SUCCESS":
        result = task.result
        response = TaskStatusResponse(
            task_id=task_id,
            status="SUCCESS",
            progress=100,
            current="Ingestion complete",
            result=result,
            session_id=UUID(result.get("session_id")) if result and "session_id" in result else None,
        )
    elif task.state == "FAILURE":
        response = TaskStatusResponse(
            task_id=task_id,
            status="FAILURE",
            progress=0,
            current="Ingestion failed",
            error=str(task.info) if task.info else "Unknown error",
        )
    else:
        response = TaskStatusResponse(
            task_id=task_id,
            status=task.state,
            current=f"Task state: {task.state}",
        )

    return response
