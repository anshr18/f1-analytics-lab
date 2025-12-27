# ============================================================================
# F1 Intelligence Hub - API Dockerfile
# Multi-stage build for development and production
# ============================================================================

# ============================================================================
# Base Stage - Common dependencies
# ============================================================================
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN pip install uv

# Set working directory
WORKDIR /app

# ============================================================================
# Development Stage
# ============================================================================
FROM base AS development

# Copy dependency files
COPY pyproject.toml README.md ./

# Install dependencies with uv
RUN uv pip install --system -e ".[dev]"

# Copy source code
COPY . .

# Set PYTHONPATH
ENV PYTHONPATH=/app/src:/libs

# Expose port
EXPOSE 8000

# Default command (overridden by docker-compose)
CMD ["uvicorn", "f1hub.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================================================
# Production Stage
# ============================================================================
FROM base AS production

# Copy dependency files
COPY pyproject.toml README.md ./

# Install only production dependencies
RUN uv pip install --system .

# Copy source code
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./

# Create non-root user
RUN useradd -m -u 1000 f1hub && chown -R f1hub:f1hub /app
USER f1hub

# Set PYTHONPATH
ENV PYTHONPATH=/app/src:/libs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn f1hub.main:app --host 0.0.0.0 --port 8000"]
