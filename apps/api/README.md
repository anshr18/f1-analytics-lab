# F1 Intelligence Hub - API

FastAPI backend for the F1 Intelligence Hub platform.

## Development

### Local Setup

```bash
# Install dependencies
cd apps/api
uv pip install -e ".[dev]"

# Run migrations
alembic upgrade head

# Start development server
uvicorn f1hub.main:app --reload
```

### Docker Setup

```bash
# From project root
docker compose up api
```

## Project Structure

```
apps/api/
├── src/f1hub/
│   ├── core/          # Config, logging, errors
│   ├── db/            # Database models and session
│   ├── api/           # FastAPI routes
│   ├── schemas/       # Pydantic request/response models
│   ├── services/      # Business logic
│   └── workers/       # Celery tasks
├── alembic/           # Database migrations
├── tests/             # pytest tests
├── pyproject.toml     # Dependencies and config
└── Dockerfile         # Multi-stage Docker build
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_api/test_health.py
```

## Code Quality

```bash
# Lint
ruff check .

# Format
black .
ruff format .

# Type check
mypy src/
```
