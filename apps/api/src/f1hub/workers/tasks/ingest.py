"""
F1 Intelligence Hub - Ingestion Tasks

Celery tasks for asynchronous data ingestion.
"""

import logging
from uuid import UUID

from celery import Task

from ...db.session import SessionLocal
from ...services.fastf1_ingest import FastF1IngestService
from ..celery_app import celery_app

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """
    Base task with database session management.

    Ensures proper session cleanup after task completion.
    """

    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        """Close database session after task completion."""
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(bind=True, base=DatabaseTask, name="ingest_session")
def ingest_session_task(self, year: int, round_number: int, session_type: str, source: str = "fastf1") -> dict:
    """
    Ingest F1 session data.

    Args:
        year: Season year
        round_number: Round number
        session_type: Session type (FP1, FP2, FP3, Q, Sprint, Race)
        source: Data source (fastf1, openf1, jolpica)

    Returns:
        Task result with session_id

    Raises:
        Exception: If ingestion fails
    """
    logger.info(f"Starting ingestion task: {year} Round {round_number} {session_type} from {source}")

    try:
        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={
                "current": "Loading session data",
                "progress": 10,
            },
        )

        # Initialize ingestion service based on source
        if source == "fastf1":
            service = FastF1IngestService(self.db)
        else:
            raise ValueError(f"Unsupported source: {source}")

        # Update state
        self.update_state(
            state="PROGRESS",
            meta={
                "current": "Parsing laps and stints",
                "progress": 30,
            },
        )

        # Run ingestion
        session_id = service.ingest_session(year, round_number, session_type)

        # Update state
        self.update_state(
            state="PROGRESS",
            meta={
                "current": "Saving to database",
                "progress": 80,
            },
        )

        logger.info(f"Ingestion task complete: session_id={session_id}")

        return {
            "session_id": str(session_id),
            "year": year,
            "round_number": round_number,
            "session_type": session_type,
            "source": source,
            "status": "success",
        }

    except Exception as e:
        logger.error(f"Ingestion task failed: {e}", exc_info=True)
        self.update_state(
            state="FAILURE",
            meta={
                "current": "Ingestion failed",
                "error": str(e),
            },
        )
        raise
