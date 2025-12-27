# Changelog

All notable changes to the F1 Intelligence Hub project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- Git branching strategy (main, dev, documentation, feature branches)
- Professional documentation (architecture.md, decisions.md)
- README with comprehensive project overview

### Infrastructure
- Docker Compose configuration for local development
- PostgreSQL 16 with pgvector extension
- Redis 7 for caching and Celery broker
- MinIO for S3-compatible object storage

### Documentation
- Architecture diagram and system overview
- Technical decision records (ADRs)
- Development workflow guidelines

## [0.1.0] - TBD (Phase 0 Target)

### Planned Features
- FastAPI backend with core routes (health, races, sessions, laps)
- SQLAlchemy database models (seasons, events, sessions, drivers, laps, stints)
- Alembic migrations for schema management
- Celery workers for async data ingestion
- FastF1 integration for lap timing data
- Next.js frontend with race selection UI
- Recharts visualization for lap times and stint strategies
- Docker Compose development environment

### Planned Endpoints
- `GET /health` - Health check
- `GET /api/v1/seasons` - List seasons
- `GET /api/v1/events` - List events
- `GET /api/v1/sessions` - List sessions
- `GET /api/v1/laps` - Get lap data
- `GET /api/v1/stints` - Get stint data
- `POST /api/v1/ingest/session` - Trigger data ingestion
- `GET /api/v1/ingest/status/{task_id}` - Check ingestion status

### Planned Tests
- Unit tests for data parsers
- Integration tests for ingestion flow
- API endpoint tests
- CI pipeline (GitHub Actions)

## Future Phases

### Phase 1 - ML Models (Q1 2025)
- Tyre degradation prediction model
- Lap time forecasting model
- Overtake probability model
- Feature engineering pipeline
- Model registry and versioning

### Phase 2 - Strategy Simulator (Q2 2025)
- Race simulation engine
- Undercut/overcut predictor
- Safety car strategy recommender
- Stint optimizer

### Phase 3 - LLM/RAG (Q3 2025)
- RAG chatbot (race engineer assistant)
- Post-race report generator
- Multi-depth explanation mode (new vs engineer)
- Strategy QA assistant

### Phase 4 - Computer Vision (Q4 2025)
- Pit stop timing from video
- Incident detection
- Track map from broadcast (stretch goal)

### Phase 5 - Live Streaming (Q1 2026)
- OpenF1 live stream integration
- Real-time predictions
- WebSocket dashboard updates

---

## Release Notes Format

Each release will include:
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

---

**Project Start Date**: 2025-12-28
**Current Phase**: Phase 0 (Foundation)
**Target Completion**: Phase 0 by Q1 2025
