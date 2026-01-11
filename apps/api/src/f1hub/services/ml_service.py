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

    def predict_lap_time(
        self,
        tyre_age: int,
        compound: str,
        track_status: str,
        position: int,
        driver_id: str,
    ) -> dict:
        """Predict lap time for given conditions.

        Args:
            tyre_age: Laps on current tyre
            compound: Tyre compound
            track_status: Track status
            position: Current position
            driver_id: Driver identifier

        Returns:
            Dictionary with prediction results
        """
        model = self.load_model("lap_time", "latest")

        # Prepare features using model's helper method
        from f1hub.ml.models.lap_time import LapTimeModel

        if isinstance(model, LapTimeModel):
            X = model.prepare_features(tyre_age, compound, track_status, position, driver_id)
        else:
            raise ValueError("Model does not support prepare_features method")

        # Predict
        lap_time_pred = model.predict(X)[0]

        return {
            "predicted_lap_time": float(lap_time_pred),
            "tyre_age": tyre_age,
            "compound": compound,
            "track_status": track_status,
            "position": position,
            "driver_id": driver_id,
            "model_version": "latest",
        }

    def predict_overtake(
        self,
        gap_seconds: float,
        closing_rate: float,
        tyre_advantage: int,
        drs_available: bool,
        lap_number: int,
    ) -> dict:
        """Predict overtake probability.

        Args:
            gap_seconds: Time gap between cars
            closing_rate: Gap change per lap
            tyre_advantage: Compound advantage
            drs_available: DRS availability
            lap_number: Current lap number

        Returns:
            Dictionary with prediction results
        """
        model = self.load_model("overtake", "latest")

        # Prepare features using model's helper method
        from f1hub.ml.models.overtake import OvertakeModel

        if isinstance(model, OvertakeModel):
            X = model.prepare_features(
                gap_seconds, closing_rate, tyre_advantage, drs_available, lap_number
            )
        else:
            raise ValueError("Model does not support prepare_features method")

        # Predict probability
        overtake_prob = model.predict(X)[0]

        return {
            "overtake_probability": float(overtake_prob),
            "gap_seconds": gap_seconds,
            "closing_rate": closing_rate,
            "tyre_advantage": tyre_advantage,
            "drs_available": drs_available,
            "lap_number": lap_number,
            "model_version": "latest",
        }

    def predict_race_result(
        self,
        grid_position: int,
        avg_lap_time: float,
        driver_id: str,
    ) -> dict:
        """Predict race finishing position.

        Args:
            grid_position: Starting position from qualifying
            avg_lap_time: Expected average lap time (seconds)
            driver_id: Driver identifier

        Returns:
            Dictionary with prediction results and top-3 probabilities
        """
        model = self.load_model("race_result", "latest")

        # Prepare features using model's helper method
        from f1hub.ml.models.race_result import RaceResultModel

        if isinstance(model, RaceResultModel):
            X = model.prepare_features(grid_position, avg_lap_time, driver_id)
        else:
            raise ValueError("Model does not support prepare_features method")

        # Predict position (already 1-indexed and rounded)
        position_pred = model.predict(X)[0]

        # For regression model, we'll provide confidence intervals instead of probabilities
        # Top 3 most likely positions are the predicted position ±1
        predicted_int = int(position_pred)
        top3_probs = {
            max(1, predicted_int - 1): 0.25,
            predicted_int: 0.50,
            min(20, predicted_int + 1): 0.25,
        }

        return {
            "predicted_position": predicted_int,
            "top3_probabilities": top3_probs,
            "grid_position": grid_position,
            "avg_lap_time": avg_lap_time,
            "driver_id": driver_id,
            "model_version": "latest",
        }

    def clear_cache(self):
        """Clear the model cache."""
        self._model_cache.clear()
        logger.info("Model cache cleared")
