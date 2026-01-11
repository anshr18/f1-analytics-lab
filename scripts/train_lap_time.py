#!/usr/bin/env python3
"""
Train Lap Time Model

Trains the lap time prediction ML model and registers it in the database.

Usage:
    python scripts/train_lap_time.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "api" / "src"))

import joblib
from minio import Minio

from f1hub.core.config import get_settings
from f1hub.db.models.models import ModelRegistry
from f1hub.db.session import SessionLocal
from f1hub.ml.models.lap_time import LapTimeModel


def main():
    """Train and register the lap time model."""
    settings = get_settings()
    db = SessionLocal()

    print("=" * 60)
    print("Training Lap Time Model")
    print("=" * 60)
    print()

    # Initialize model
    model = LapTimeModel()

    # Load training data
    print("1. Loading training data from database...")
    try:
        X, y = model.load_training_data(db)
        print(f"   ✓ Loaded {len(X)} lap samples")
        print(f"   ✓ Mean lap time: {y.mean():.3f}s, Std: {y.std():.3f}s")
        print()
    except ValueError as e:
        print(f"   ✗ Error: {e}")
        print("   Make sure lap features are computed first.")
        db.close()
        sys.exit(1)

    # Train model
    print("2. Training model...")
    metrics = model.train(X, y)
    print(f"   ✓ Training complete!")
    print(f"   ✓ RMSE: {metrics['rmse']:.3f} seconds")
    print(f"   ✓ MAE: {metrics['mae']:.3f} seconds")
    print(f"   ✓ R²: {metrics['r2']:.4f}")
    print(f"   ✓ Train samples: {metrics['train_samples']}")
    print(f"   ✓ Test samples: {metrics['test_samples']}")
    print()

    # Save model locally
    version = "1.0.0"
    model_filename = f"lap_time_v{version}.pkl"
    local_path = f"/tmp/{model_filename}"

    print(f"3. Saving model to {local_path}...")
    joblib.dump(model, local_path)
    print("   ✓ Model saved")
    print()

    # Upload to MinIO
    print("4. Uploading model to MinIO...")
    try:
        minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=settings.MINIO_USE_SSL,
        )

        # Ensure models bucket exists
        if not minio_client.bucket_exists("models"):
            minio_client.make_bucket("models")

        # Upload model
        artifact_path = f"lap_time/{version}/{model_filename}"
        minio_client.fput_object("models", artifact_path, local_path)
        print(f"   ✓ Uploaded to models/{artifact_path}")
        print()
    except Exception as e:
        print(f"   ✗ MinIO upload failed: {e}")
        db.close()
        sys.exit(1)

    # Register in database
    print("5. Registering model in database...")
    try:
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

        print(f"   ✓ Model registered with ID: {registry_entry.id}")
        print()
    except Exception as e:
        print(f"   ✗ Database registration failed: {e}")
        db.rollback()
        db.close()
        sys.exit(1)

    print("=" * 60)
    print("✓ Training Complete!")
    print("=" * 60)
    print()
    print(f"  - Model ID: {registry_entry.id}")
    print(f"  - Version: {version}")
    print(f"  - RMSE: {metrics['rmse']:.3f} seconds (Target: < 0.5s)")
    print()

    db.close()


if __name__ == "__main__":
    main()
