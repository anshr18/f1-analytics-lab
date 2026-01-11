"""
Model Registry API Endpoints

Endpoints for managing ML models in the registry.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from f1hub.core.dependencies import get_db
from f1hub.db.models.models import ModelRegistry
from f1hub.schemas.models import (
    ModelListResponse,
    ModelResponse,
    ModelTrainingRequest,
    ModelTrainingResponse,
    TaskStatusResponse,
)

router = APIRouter(prefix="/models")


@router.get("", response_model=ModelListResponse)
async def list_models(
    db: Session = Depends(get_db),
    model_name: str | None = None,
    status: str | None = None,
) -> ModelListResponse:
    """List all registered models.

    Args:
        db: Database session
        model_name: Optional filter by model name
        status: Optional filter by status (active, archived)

    Returns:
        List of models with metadata
    """
    query = db.query(ModelRegistry)

    if model_name:
        query = query.filter(ModelRegistry.model_name == model_name)
    if status:
        query = query.filter(ModelRegistry.status == status)

    models = query.order_by(ModelRegistry.created_at.desc()).all()

    return ModelListResponse(
        models=[ModelResponse.model_validate(m) for m in models],
        total=len(models),
    )


@router.get("/{model_id}", response_model=ModelResponse)
async def get_model(
    model_id: UUID,
    db: Session = Depends(get_db),
) -> ModelResponse:
    """Get model details by ID.

    Args:
        model_id: Model UUID
        db: Database session

    Returns:
        Model metadata

    Raises:
        HTTPException: If model not found
    """
    model = db.query(ModelRegistry).filter(ModelRegistry.id == model_id).first()

    if not model:
        raise HTTPException(status_code=404, detail="Model not found")

    return ModelResponse.model_validate(model)


@router.post("/train", response_model=ModelTrainingResponse)
async def trigger_training(
    request: ModelTrainingRequest,
    db: Session = Depends(get_db),
) -> ModelTrainingResponse:
    """Trigger async model training.

    Args:
        request: Training request with model name and parameters
        db: Database session

    Returns:
        Training task information

    Raises:
        HTTPException: If model name is invalid
    """
    from f1hub.workers.tasks.ml import (
        train_lap_time_task,
        train_overtake_task,
        train_race_result_task,
        train_tyre_degradation_task,
    )

    # Map model names to Celery tasks
    task_map = {
        "tyre_degradation": train_tyre_degradation_task,
        "lap_time": train_lap_time_task,
        "overtake": train_overtake_task,
        "race_result": train_race_result_task,
    }

    if request.model_name not in task_map:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model name. Must be one of: {', '.join(task_map.keys())}",
        )

    # Trigger Celery task
    task = task_map[request.model_name].delay()

    return ModelTrainingResponse(
        task_id=task.id,
        model_name=request.model_name,
        status="pending",
        message=f"Training task started for {request.model_name}",
    )


@router.get("/train/{task_id}", response_model=TaskStatusResponse)
async def get_training_status(task_id: str) -> TaskStatusResponse:
    """Get training task status.

    Args:
        task_id: Celery task ID

    Returns:
        Task status information
    """
    from celery.result import AsyncResult

    from f1hub.workers.celery_app import celery_app

    task = AsyncResult(task_id, app=celery_app)

    response = TaskStatusResponse(
        task_id=task_id,
        status=task.state,
        result=task.result if task.ready() else None,
        error=str(task.info) if task.failed() else None,
    )

    # Add progress info if available
    if task.state == "PROGRESS" and isinstance(task.info, dict):
        response.progress = task.info.get("status")

    return response
