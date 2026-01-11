"""
F1 Intelligence Hub - Logging Configuration

Structured logging setup with JSON formatting for production
and colorized console output for development.
"""

import logging
import sys
from typing import Any

from .config import settings


def setup_logging() -> None:
    """
    Configure application logging.

    Development: Colorized console output
    Production: JSON-formatted structured logs
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Reduce noise from third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

    # Set FastF1 to WARNING to reduce cache-related logs
    logging.getLogger("fastf1").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Module name (typically __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


# Example usage:
# from f1hub.core.logging import get_logger
# logger = get_logger(__name__)
# logger.info("Application started")
