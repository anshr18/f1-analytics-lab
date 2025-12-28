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

    This endpoint will trigger a Celery task to train the model.
    In Week 2, we return a placeholder response. Celery integration
    will be added in Week 3.

    Args:
        request: Training request with model name and parameters
        db: Database session

    Returns:
        Training task information
    """
    # TODO: Implement Celery task in Week 3
    # from f1hub.workers.tasks.ml import train_model_task
    # task = train_model_task.delay(request.model_name, request.parameters)

    return ModelTrainingResponse(
        task_id="placeholder-task-id",
        model_name=request.model_name,
        status="pending",
        message=f"Training for {request.model_name} will be implemented in Week 3",
    )
