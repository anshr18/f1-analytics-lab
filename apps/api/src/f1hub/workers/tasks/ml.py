"""
ML Training Celery Tasks

Async tasks for training ML models.
"""

import logging
from pathlib import Path
from uuid import UUID

import joblib
from minio import Minio

from f1hub.core.config import get_settings
from f1hub.db.models.models import ModelRegistry
from f1hub.db.session import SessionLocal
from f1hub.ml.models import (
    LapTimeModel,
    OvertakeModel,
    RaceResultModel,
    TyreDegradationModel,
)
from f1hub.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="train_tyre_degradation")
def train_tyre_degradation_task(self):
    """Train tyre degradation model."""
    self.update_state(state="PROGRESS", meta={"status": "Initializing tyre degradation model..."})

    db = SessionLocal()
    settings = get_settings()

    try:
        logger.info("Starting tyre degradation model training")

        # Initialize model
        model = TyreDegradationModel()

        # Load training data
        self.update_state(state="PROGRESS", meta={"status": "Loading training data..."})
        X, y = model.load_training_data(db)
        logger.info(f"Loaded {len(X)} training samples")

        # Train model
        self.update_state(state="PROGRESS", meta={"status": "Training model..."})
        metrics = model.train(X, y)
        logger.info(f"Training complete. Metrics: {metrics}")

        # Save model locally
        version = "1.0.0"
        model_filename = f"tyre_degradation_v{version}.pkl"
        local_path = f"/tmp/{model_filename}"

        self.update_state(state="PROGRESS", meta={"status": "Saving model..."})
        joblib.dump(model, local_path)

        # Upload to MinIO
        self.update_state(state="PROGRESS", meta={"status": "Uploading to MinIO..."})
        minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_USE_SSL,
        )

        if not minio_client.bucket_exists("models"):
            minio_client.make_bucket("models")

        artifact_path = f"tyre_degradation/{version}/{model_filename}"
        minio_client.fput_object("models", artifact_path, local_path)

        # Register in database
        self.update_state(state="PROGRESS", meta={"status": "Registering model..."})
        registry_entry = ModelRegistry(
            model_name="tyre_degradation",
            version=version,
            model_type="regression",
            status="active",
            metrics=metrics,
            artifact_path=artifact_path,
        )

        db.add(registry_entry)
        db.commit()
        db.refresh(registry_entry)

        logger.info(f"Model registered with ID: {registry_entry.id}")

        return {
            "model_id": str(registry_entry.id),
            "model_name": "tyre_degradation",
            "version": version,
            "metrics": metrics,
        }

    except Exception as e:
        logger.error(f"Training failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(bind=True, name="train_lap_time")
def train_lap_time_task(self):
    """Train lap time model."""
    self.update_state(state="PROGRESS", meta={"status": "Initializing lap time model..."})

    db = SessionLocal()
    settings = get_settings()

    try:
        logger.info("Starting lap time model training")

        model = LapTimeModel()

        self.update_state(state="PROGRESS", meta={"status": "Loading training data..."})
        X, y = model.load_training_data(db)
        logger.info(f"Loaded {len(X)} training samples")

        self.update_state(state="PROGRESS", meta={"status": "Training model..."})
        metrics = model.train(X, y)
        logger.info(f"Training complete. Metrics: {metrics}")

        version = "1.0.0"
        model_filename = f"lap_time_v{version}.pkl"
        local_path = f"/tmp/{model_filename}"

        self.update_state(state="PROGRESS", meta={"status": "Saving model..."})
        joblib.dump(model, local_path)

        self.update_state(state="PROGRESS", meta={"status": "Uploading to MinIO..."})
        minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_USE_SSL,
        )

        if not minio_client.bucket_exists("models"):
            minio_client.make_bucket("models")

        artifact_path = f"lap_time/{version}/{model_filename}"
        minio_client.fput_object("models", artifact_path, local_path)

        self.update_state(state="PROGRESS", meta={"status": "Registering model..."})
        registry_entry = ModelRegistry(
            model_name="lap_time",
            version=version,
            model_type="regression",
            status="active",
            metrics=metrics,
            artifact_path=artifact_path,
        )

        db.add(registry_entry)
        db.commit()
        db.refresh(registry_entry)

        logger.info(f"Model registered with ID: {registry_entry.id}")

        return {
            "model_id": str(registry_entry.id),
            "model_name": "lap_time",
            "version": version,
            "metrics": metrics,
        }

    except Exception as e:
        logger.error(f"Training failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(bind=True, name="train_overtake")
def train_overtake_task(self):
    """Train overtake model."""
    self.update_state(state="PROGRESS", meta={"status": "Initializing overtake model..."})

    db = SessionLocal()
    settings = get_settings()

    try:
        logger.info("Starting overtake model training")

        model = OvertakeModel()

        self.update_state(state="PROGRESS", meta={"status": "Loading training data..."})
        X, y = model.load_training_data(db)
        logger.info(f"Loaded {len(X)} training samples")

        self.update_state(state="PROGRESS", meta={"status": "Training model..."})
        metrics = model.train(X, y)
        logger.info(f"Training complete. Metrics: {metrics}")

        version = "1.0.0"
        model_filename = f"overtake_v{version}.pkl"
        local_path = f"/tmp/{model_filename}"

        self.update_state(state="PROGRESS", meta={"status": "Saving model..."})
        joblib.dump(model, local_path)

        self.update_state(state="PROGRESS", meta={"status": "Uploading to MinIO..."})
        minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_USE_SSL,
        )

        if not minio_client.bucket_exists("models"):
            minio_client.make_bucket("models")

        artifact_path = f"overtake/{version}/{model_filename}"
        minio_client.fput_object("models", artifact_path, local_path)

        self.update_state(state="PROGRESS", meta={"status": "Registering model..."})
        registry_entry = ModelRegistry(
            model_name="overtake",
            version=version,
            model_type="classification",
            status="active",
            metrics=metrics,
            artifact_path=artifact_path,
        )

        db.add(registry_entry)
        db.commit()
        db.refresh(registry_entry)

        logger.info(f"Model registered with ID: {registry_entry.id}")

        return {
            "model_id": str(registry_entry.id),
            "model_name": "overtake",
            "version": version,
            "metrics": metrics,
        }

    except Exception as e:
        logger.error(f"Training failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(bind=True, name="train_race_result")
def train_race_result_task(self):
    """Train race result model."""
    self.update_state(state="PROGRESS", meta={"status": "Initializing race result model..."})

    db = SessionLocal()
    settings = get_settings()

    try:
        logger.info("Starting race result model training")

        model = RaceResultModel()

        self.update_state(state="PROGRESS", meta={"status": "Loading training data..."})
        X, y = model.load_training_data(db)
        logger.info(f"Loaded {len(X)} training samples")

        self.update_state(state="PROGRESS", meta={"status": "Training model..."})
        metrics = model.train(X, y)
        logger.info(f"Training complete. Metrics: {metrics}")

        version = "1.0.0"
        model_filename = f"race_result_v{version}.pkl"
        local_path = f"/tmp/{model_filename}"

        self.update_state(state="PROGRESS", meta={"status": "Saving model..."})
        joblib.dump(model, local_path)

        self.update_state(state="PROGRESS", meta={"status": "Uploading to MinIO..."})
        minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_USE_SSL,
        )

        if not minio_client.bucket_exists("models"):
            minio_client.make_bucket("models")

        artifact_path = f"race_result/{version}/{model_filename}"
        minio_client.fput_object("models", artifact_path, local_path)

        self.update_state(state="PROGRESS", meta={"status": "Registering model..."})
        registry_entry = ModelRegistry(
            model_name="race_result",
            version=version,
            model_type="regression",
            status="active",
            metrics=metrics,
            artifact_path=artifact_path,
        )

        db.add(registry_entry)
        db.commit()
        db.refresh(registry_entry)

        logger.info(f"Model registered with ID: {registry_entry.id}")

        return {
            "model_id": str(registry_entry.id),
            "model_name": "race_result",
            "version": version,
            "metrics": metrics,
        }

    except Exception as e:
        logger.error(f"Training failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()
