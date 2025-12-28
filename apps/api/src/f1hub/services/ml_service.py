"""
ML Service

Handles model loading, caching, and inference.
"""

import logging
import os
from typing import Dict
from uuid import UUID

import joblib
from minio import Minio
from sqlalchemy.orm import Session

from f1hub.db.models.models import ModelRegistry
from f1hub.db.models.timing import Stint
from f1hub.ml.base import BaseMLModel

logger = logging.getLogger(__name__)


class MLService:
    """Handles model loading and inference.

    Models are loaded from MinIO and cached in memory for fast inference.
    """

    def __init__(self, db: Session, minio_client: Minio):
        """Initialize ML service.

        Args:
            db: Database session
            minio_client: MinIO client for object storage
        """
        self.db = db
        self.minio = minio_client
        self._model_cache: Dict[str, BaseMLModel] = {}

    def load_model(self, model_name: str, version: str = "latest") -> BaseMLModel:
        """Load model from MinIO or cache.

        Args:
            model_name: Name of the model (e.g., "tyre_degradation")
            version: Model version or "latest"

        Returns:
            Loaded model instance

        Raises:
            ValueError: If model not found in registry
        """
        cache_key = f"{model_name}:{version}"

        # Check cache first
        if cache_key in self._model_cache:
            logger.debug(f"Loading model {cache_key} from cache")
            return self._model_cache[cache_key]

        # Get model metadata from registry
        if version == "latest":
            model_entry = (
                self.db.query(ModelRegistry)
                .filter(
                    ModelRegistry.model_name == model_name,
                    ModelRegistry.status == "active",
                )
                .order_by(ModelRegistry.created_at.desc())
                .first()
            )
        else:
            model_entry = (
                self.db.query(ModelRegistry)
                .filter(
                    ModelRegistry.model_name == model_name,
                    ModelRegistry.version == version,
                )
                .first()
            )

        if not model_entry:
            raise ValueError(f"Model {model_name}:{version} not found in registry")

        # Download from MinIO
        model_path = f"/tmp/{model_name}_{version}.pkl"
        logger.info(f"Downloading model {cache_key} from MinIO: {model_entry.artifact_path}")

        try:
            self.minio.fget_object(
                "models",
                model_entry.artifact_path,
                model_path,
            )
        except Exception as e:
            logger.error(f"Failed to download model from MinIO: {e}")
            raise ValueError(f"Failed to download model {cache_key}: {e}")

        # Load with joblib
        try:
            model = joblib.load(model_path)
            self._model_cache[cache_key] = model
            logger.info(f"Model {cache_key} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise ValueError(f"Failed to load model {cache_key}: {e}")
        finally:
            # Clean up temp file
            if os.path.exists(model_path):
                os.remove(model_path)

        return model

    def predict_tyre_degradation(self, stint_id: UUID) -> dict:
        """Predict degradation for a stint.

        Args:
            stint_id: Stint UUID

        Returns:
            Dictionary with prediction results
        """
        model = self.load_model("tyre_degradation", "latest")

        # Get stint data
        stint = self.db.query(Stint).filter(Stint.id == stint_id).first()

        if not stint:
            raise ValueError(f"Stint {stint_id} not found")

        # Prepare features using model's helper method
        from f1hub.ml.models.tyre_degradation import TyreDegradationModel

        if isinstance(model, TyreDegradationModel):
            X = model.prepare_features(stint.compound, stint.driver_id)
        else:
            raise ValueError("Model does not support prepare_features method")

        # Predict
        deg_pred = model.predict(X)[0]

        return {
            "stint_id": str(stint_id),
            "predicted_deg_per_lap": float(deg_pred),
            "compound": stint.compound,
            "driver_id": stint.driver_id,
            "model_version": "latest",
        }

    def clear_cache(self):
        """Clear the model cache."""
        self._model_cache.clear()
        logger.info("Model cache cleared")
