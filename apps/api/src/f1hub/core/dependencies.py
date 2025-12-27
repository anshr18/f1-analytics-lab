"""
F1 Intelligence Hub - FastAPI Dependencies

Dependency injection functions for FastAPI routes.
"""

from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from .config import Settings, get_settings
from ..db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.

    Yields a SQLAlchemy session and ensures it's closed after use.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_settings_dependency() -> Settings:
    """
    Settings dependency.

    Returns:
        Settings: Application settings

    Example:
        @router.get("/config")
        def get_config(settings: Settings = Depends(get_settings_dependency)):
            return {"environment": settings.ENVIRONMENT}
    """
    return get_settings()


# Placeholder for Phase 3 authentication
def get_current_user():
    """
    Get current authenticated user.

    This is a placeholder for Phase 3 when authentication is implemented.
    For Phase 0, all endpoints are public.

    Returns:
        None: No authentication in Phase 0
    """
    return None
