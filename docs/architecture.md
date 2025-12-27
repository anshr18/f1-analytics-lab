# F1 Intelligence Hub - Architecture

## System Overview

The F1 Intelligence Hub is a modular analytics platform built as a monorepo web application that unifies Formula 1 data from multiple sources into a single schema, enabling advanced ML predictions, strategy simulations, and LLM-powered insights.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │Dashboard │  │ Strategy │  │   Chat   │  │  Live    │        │
│  │  View    │  │Simulator │  │ (RAG)    │  │ Timing   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              │
                     REST API (JSON)
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     API Routes                            │   │
│  │  /races  /sessions  /laps  /ingest  /predict  /chat      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   Service Layer                           │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │   │
│  │  │ Ingest   │  │Features  │  │   ML     │  │   LLM    │ │   │
│  │  │ Service  │  │ Builder  │  │ Service  │  │  (RAG)   │ │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
       ┌────────────▼──────┐   ┌────────▼────────┐
       │  Celery Workers   │   │  PostgreSQL     │
       │  (Async Tasks)    │   │  + pgvector     │
       │                   │   │                 │
       │  - Ingestion      │   │  - Raw Data     │
       │  - Training       │   │  - Features     │
       │  - Embeddings     │   │  - Models       │
       │  - Video (Phase4) │   │  - Embeddings   │
       └───────────────────┘   └─────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     Data Sources                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                       │
│  │ FastF1   │  │ OpenF1   │  │ Jolpica  │                       │
│  │(Telemetry│  │  (Live   │  │(Historic │                       │
│  │  + Laps) │  │  API)    │  │Metadata) │                       │
│  └──────────┘  └──────────┘  └──────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **State Management**: React hooks + Server Components
- **API Client**: Native Fetch API

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Async Tasks**: Celery
- **Validation**: Pydantic v2
- **Package Manager**: uv (fast dependency resolution)

### Database & Storage
- **Primary DB**: PostgreSQL 16
- **Vector Extension**: pgvector (for embeddings)
- **Cache/Broker**: Redis 7
- **Object Storage**: MinIO (S3-compatible)

### Data Sources
- **FastF1**: Lap timing + telemetry (primary)
- **OpenF1**: Real-time API + live streaming
- **Jolpica**: Historical results metadata (Ergast replacement)

### Infrastructure
- **Development**: Docker Compose
- **CI/CD**: GitHub Actions
- **Linting**: Ruff (Python), ESLint (TS)
- **Formatting**: Black (Python), Prettier (TS)
- **Type Checking**: mypy (Python), TypeScript compiler

## Directory Structure

```
f1-analytics-lab/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── src/f1hub/
│   │   │   ├── core/          # Config, logging, errors
│   │   │   ├── db/            # SQLAlchemy models
│   │   │   ├── api/           # FastAPI routes
│   │   │   ├── schemas/       # Pydantic schemas
│   │   │   ├── services/      # Business logic
│   │   │   └── workers/       # Celery tasks
│   │   ├── alembic/           # Database migrations
│   │   ├── tests/             # Pytest tests
│   │   └── Dockerfile
│   │
│   └── web/                    # Next.js frontend
│       ├── src/
│       │   ├── app/           # Pages (App Router)
│       │   ├── components/    # React components
│       │   ├── lib/           # Utilities + API client
│       │   └── types/         # TypeScript types
│       └── Dockerfile
│
├── libs/                       # Shared libraries
│   ├── f1data/                # Data clients + parsers
│   ├── sim/                   # Strategy simulator (Phase 2)
│   ├── common/                # Shared utilities
│   └── mlcore/                # ML features + metrics (Phase 1)
│
├── docs/                       # Documentation
│   ├── architecture.md        # This file
│   ├── decisions.md           # Technical decisions (ADRs)
│   └── screenshots/           # Demo screenshots
│
├── scripts/                    # Helper scripts
│   ├── dev_up.sh
│   ├── dev_down.sh
│   └── seed_demo_data.py
│
├── data/                       # Local development data (gitignored)
│   ├── raw/
│   ├── processed/
│   └── fastf1_cache/
│
├── models/                     # Trained model artifacts (gitignored)
│
├── .github/
│   └── workflows/
│       ├── api_ci.yml         # Backend CI
│       └── web_ci.yml         # Frontend CI
│
├── docker-compose.yml          # Multi-service orchestration
├── Makefile                    # Common dev commands
├── .env.example                # Environment variables template
└── CHANGELOG.md                # Release history
```

## Data Flow

### Phase 0: Ingestion & Visualization

```
1. User selects race in frontend
2. Frontend calls POST /api/v1/ingest/session
3. API enqueues Celery task
4. Celery worker:
   - Fetches data from FastF1
   - Parses laps, stints, race control messages
   - Normalizes to internal schema
   - Inserts into PostgreSQL
   - Marks session as ingested
5. Frontend polls GET /api/v1/ingest/status/{task_id}
6. When complete, frontend fetches laps and stints
7. Charts render using Recharts
```

---

**Last Updated**: 2025-12-28
**Phase**: 0 (Foundation)
**Status**: In Development
