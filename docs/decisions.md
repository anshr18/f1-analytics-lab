# Technical Decisions

This document captures key architectural and technical decisions made during the development of F1 Intelligence Hub. Each decision includes context, the choice made, and the rationale.

---

## ADR-001: Monorepo Structure

**Date**: 2025-12-28
**Status**: Accepted

### Context
Need to organize backend, frontend, and shared libraries in a maintainable way.

### Decision
Use a monorepo with `apps/` (deployable applications) and `libs/` (shared code).

### Rationale
- Shared code (data clients, utilities) can be imported by both API and workers
- Easier dependency management and versioning
- Atomic commits across frontend + backend
- Simpler than managing multiple repositories for a solo project

### Alternatives Considered
- Separate repos for API/web
- Rejected: More overhead for a single developer, harder to coordinate changes

---

## ADR-002: Python Package Manager (uv)

**Date**: 2025-12-28
**Status**: Accepted

### Context
Need fast, reliable Python dependency management.

### Decision
Use `uv` instead of pip or poetry.

### Rationale
- 10-100x faster than pip
- Built-in lockfile support (uv.lock)
- Modern dependency resolution
- Growing community adoption
- Compatible with pyproject.toml standard

### Alternatives Considered
- pip + pip-tools: Too slow for development iteration
- poetry: Good, but slower than uv
- pdm: Less mature ecosystem

---

## ADR-003: Database Primary Keys (UUIDs)

**Date**: 2025-12-28
**Status**: Accepted

### Context
Need to choose primary key strategy for all database tables.

### Decision
Use UUIDs (UUID v4) for all entity primary keys.

### Rationale
- Avoids sequential ID exposure (security)
- Easier to merge data from multiple sources
- Better for distributed systems (future-proofing)
- No coordination needed for ID generation

### Trade-offs
- Slightly larger index sizes (~16 bytes vs 4-8 bytes)
- Less human-readable in logs
- Acceptable trade-off for this scale

---

## ADR-004: Lap Time Storage (PostgreSQL interval)

**Date**: 2025-12-28
**Status**: Accepted

### Context
Need to store lap times and sector times.

### Decision
Use PostgreSQL `interval` type instead of float or integer milliseconds.

### Rationale
- Semantically correct for durations
- Native time arithmetic (lap1 - lap2)
- Prevents unit confusion (seconds vs milliseconds)
- Easier to query and aggregate

### Trade-offs
- Slightly more complex serialization to JSON
- Worth it for data integrity and query simplicity

---

## ADR-005: Celery for Async Tasks

**Date**: 2025-12-28
**Status**: Accepted

### Context
Data ingestion from FastF1 can take 30s-2min. Cannot block API requests.

### Decision
Use Celery with Redis as broker for all long-running tasks.

### Rationale
- Battle-tested distributed task queue
- Supports retries, task chaining, progress tracking
- Redis already needed for caching
- Scales horizontally (add more workers)

### Alternatives Considered
- FastAPI BackgroundTasks: Not suitable for >30s tasks, no persistence
- RQ (Redis Queue): Less feature-rich than Celery
- ARQ (async): Too new, smaller ecosystem

---

## ADR-006: FastF1 as Primary Data Source

**Date**: 2025-12-28
**Status**: Accepted

### Context
Need to ingest F1 timing and telemetry data.

### Decision
Use FastF1 as the primary data source for Phase 0.

### Rationale
- Most comprehensive telemetry data (speed, throttle, brake, DRS)
- Well-maintained open-source library
- Returns pandas DataFrames (ML-friendly)
- Large community, good documentation
- Free and legal

### Alternatives Considered
- OpenF1: Good for live data, but less historical depth
- Jolpica: Only metadata, no telemetry
- Commercial APIs: Too expensive for portfolio project

---

## ADR-007: Next.js App Router

**Date**: 2025-12-28
**Status**: Accepted

### Context
Next.js has two routing systems: Pages Router and App Router.

### Decision
Use App Router (Next.js 13+).

### Rationale
- Modern Next.js standard
- Better TypeScript support
- React Server Components ready (future optimization)
- Clearer mental model (folders = routes)
- Better file colocation

### Alternatives Considered
- Pages Router: Stable, but legacy

---

## ADR-008: Recharts for Visualization

**Date**: 2025-12-28
**Status**: Accepted

### Context
Need a charting library for lap time and stint visualization.

### Decision
Use Recharts.

### Rationale
- React-native API (declarative, composable)
- Good TypeScript support
- Free and open-source
- Sufficient for Phase 0 requirements
- Easy to customize

### Alternatives Considered
- Chart.js: More features, but imperative API
- D3.js: Too complex for initial needs
- Plotly: Overkill for simple line/bar charts

---

## ADR-009: Docker Compose for Local Development

**Date**: 2025-12-28
**Status**: Accepted

### Context
Need to run Postgres, Redis, MinIO, API, Worker, and Web services locally.

### Decision
Use Docker Compose for local development.

### Rationale
- One-command startup (`docker compose up`)
- Consistent environment across machines
- Easy to share and document
- Production-like setup
- All services networked automatically

### Alternatives Considered
- Native installation: Harder to document, inconsistent across machines
- Kubernetes (local): Overkill for development

---

## ADR-010: pgvector for Embeddings

**Date**: 2025-12-28
**Status**: Accepted

### Context
Phase 3 will need vector embeddings for RAG (LLM chatbot).

### Decision
Use pgvector extension for PostgreSQL.

### Rationale
- Keeps everything in one database (no separate vector DB)
- Good enough performance for Phase 0-3 scale
- Native SQL queries with vector similarity
- Open-source and well-maintained
- Easy to migrate to dedicated vector DB later if needed

### Alternatives Considered
- Pinecone: Commercial, requires API key
- Weaviate: Requires separate service
- Qdrant: Requires separate service

---

## ADR-011: Separate Stints Table

**Date**: 2025-12-28
**Status**: Accepted

### Context
Need to model tyre stints (consecutive laps on same compound).

### Decision
Create a separate `stints` table instead of just grouping laps.

### Rationale
- Stint is a distinct strategic concept in F1
- Makes querying stint-level metrics easier
- Allows storing stint metadata (tyre age at start, etc.)
- Each lap still has stint_id FK for easy join

### Alternatives Considered
- Compute stints on-the-fly from laps: Slower queries, no metadata storage

---

## ADR-012: Feature Store Pattern

**Date**: 2025-12-28
**Status**: Accepted

### Context
Phase 1 ML models will need engineered features.

### Decision
Create separate feature tables (lap_features, stint_features, battle_features).

### Rationale
- Keeps raw data immutable
- Allows feature evolution without reingesting
- Supports multiple feature versions
- Easier to debug feature engineering logic
- Standard ML engineering pattern

### Alternatives Considered
- Compute features on-the-fly: Too slow, hard to version

---

## ADR-013: Alembic for Migrations Only

**Date**: 2025-12-28
**Status**: Accepted

### Context
Need database schema versioning and evolution.

### Decision
Use Alembic for all schema changes, never manual SQL edits.

### Rationale
- Reproducible migrations
- Easy rollbacks
- Version controlled
- Required for team collaboration (even solo, good practice)
- Ensures consistency across environments

### Alternatives Considered
- Manual SQL scripts: Error-prone, hard to track

---

## ADR-014: Professional Git Workflow (Solo)

**Date**: 2025-12-28
**Status**: Accepted

### Context
Building a portfolio project to showcase engineering skills.

### Decision
Use a structured branching strategy even though working solo:
- `main` = stable
- `dev` = integration branch
- `documentation` = all docs
- `feature/*` = individual features
- `fix/*` = bug fixes

Commit format:
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `test:` tests
- `refactor:` code cleanup
- `chore:` config/tooling

### Rationale
- Demonstrates professional software engineering practices
- Clean git history for recruiters to review
- Forces small, focused commits
- Easy to showcase specific features
- Industry-standard workflow

---

## ADR-015: Tailwind CSS for Styling

**Date**: 2025-12-28
**Status**: Accepted

### Context
Need a styling approach for the Next.js frontend.

### Decision
Use Tailwind CSS utility-first framework.

### Rationale
- Fast development iteration
- Consistent design system out of the box
- No CSS file sprawl
- Easy to customize
- Widely adopted (good for resume)

### Alternatives Considered
- CSS Modules: More boilerplate
- Styled Components: Runtime overhead
- Plain CSS: Harder to maintain consistency

---

## Future Decisions (To Be Documented)

- ADR-016: ML framework choice (scikit-learn vs PyTorch)
- ADR-017: LLM provider (OpenAI vs Anthropic vs local)
- ADR-018: Authentication strategy (OAuth2 vs JWT)
- ADR-019: Deployment platform (AWS vs GCP vs Vercel)

---

**Last Updated**: 2025-12-28
