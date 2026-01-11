"""
F1 Intelligence Hub - FastAPI Application

Main application entry point with middleware, CORS, and exception handlers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.errors import (
    DataNotFoundError,
    ExternalAPIError,
    F1HubException,
    ValidationError,
    data_not_found_handler,
    external_api_error_handler,
    f1hub_exception_handler,
    validation_error_handler,
)
from .core.logging import get_logger, setup_logging

# Configure logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    yield

    # Shutdown
    logger.info("Shutting down F1 Intelligence Hub")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="F1 analytics platform with ML, LLM, and live streaming capabilities",
    docs_url="/docs" if settings.ENABLE_SWAGGER_UI else None,
    redoc_url="/redoc" if settings.ENABLE_REDOC else None,
    lifespan=lifespan,
)

# ============================================================================
# Middleware
# ============================================================================

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Exception Handlers
# ============================================================================

app.add_exception_handler(F1HubException, f1hub_exception_handler)
app.add_exception_handler(DataNotFoundError, data_not_found_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(ExternalAPIError, external_api_error_handler)

# ============================================================================
# Routes
# ============================================================================

# Health check endpoint (no prefix)
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.

    Returns basic application status and version information.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }
    )


# Root redirect
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.

    Redirects to API documentation.
    """
    return JSONResponse(
        content={
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
        }
    )


# API v1 routes
from .api.router import api_router

app.include_router(api_router, prefix=settings.API_PREFIX)
