"""
F1 Intelligence Hub - ML Model Registry Database Models

Model registry and predictions: ModelRegistry, Prediction
"""

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from ..base import Base
from .base import TimestampMixin, UUIDPrimaryKeyMixin


class ModelRegistry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    ML Model Registry.

    Tracks trained models, their versions, and performance metrics.
    """

    __tablename__ = "model_registry"

    model_name = Column(String(100), nullable=False)  # e.g., "lap_time_predictor_v1"
    version = Column(String(50), nullable=False)  # e.g., "1.0.0", "2024-03-15"
    model_type = Column(String(50), nullable=False)  # regression, classification, clustering
    description = Column(Text, nullable=True)

    # Performance metrics (stored as JSON)
    metrics = Column(JSONB, nullable=True)  # {"rmse": 0.5, "mae": 0.3, "r2": 0.95}

    # Artifact storage
    artifact_path = Column(String(500), nullable=True)  # S3/MinIO path to model file
    training_config = Column(JSONB, nullable=True)  # Hyperparameters, features used, etc.

    # Status
    status = Column(String(20), nullable=False, default="training")  # training, active, deprecated

    # Relationships
    predictions = relationship("Prediction", back_populates="model", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ModelRegistry(name={self.model_name}, version={self.version}, status={self.status})>"


class Prediction(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Model Prediction.

    Stores predictions made by ML models.
    """

    __tablename__ = "predictions"

    model_id = Column(UUID(as_uuid=True), ForeignKey("model_registry.id"), nullable=False)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=True)  # Null for general predictions
    prediction_type = Column(String(50), nullable=False)  # lap_time, race_result, overtake_probability, etc.

    # Input features (for reproducibility)
    input_features = Column(JSONB, nullable=True)

    # Prediction output
    prediction_value = Column(JSONB, nullable=False)  # Flexible JSON for different prediction types

    # Confidence/probability
    confidence = Column(JSONB, nullable=True)  # {"mean": 90.5, "std": 1.2, "intervals": [...]}

    # Relationships
    model = relationship("ModelRegistry", back_populates="predictions")

    def __repr__(self) -> str:
        return f"<Prediction(model_id={self.model_id}, type={self.prediction_type})>"
