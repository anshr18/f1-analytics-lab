# F1 Intelligence Hub 🏎️📊

> A full-stack Formula 1 analytics platform combining data engineering, machine learning, and modern web development to deliver race insights, strategy predictions, and intelligent analysis.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![TypeScript](https://img.shields.io/badge/typescript-5.0+-blue.svg)](https://www.typescriptlang.org/)
[![Phase](https://img.shields.io/badge/phase-1%20(ML%20Predictions)-green.svg)](#project-phases)

## 🎯 Project Overview

F1 Intelligence Hub is a **production-grade monorepo** that unifies Formula 1 data from multiple sources into a single analytics platform. Built to showcase full-stack development, data engineering, and ML engineering skills.

**Current Status**: ✅ Phase 1 - ML Predictions (COMPLETE!)

### 🚀 Key Features

**Phase 0 (✅ COMPLETE)**:
- **📊 Data Ingestion Pipeline**: Automated ETL from FastF1 with Celery workers
- **💾 Database Layer**: PostgreSQL with pgvector, 18 tables, complete schema
- **🌐 REST API**: 15+ FastAPI endpoints with OpenAPI docs
- **📈 Interactive Dashboard**: Next.js 15 with Recharts, lap/stint visualization
- **🔄 One-Button Workflow**: Select race → Ingest → Visualize

**Phase 1 (✅ COMPLETE)**:
- **🤖 Feature Engineering**: 3 feature tables (lap, stint, battle) with 1,400+ computed features
- **🎯 ML Models**: 4 trained models (tyre degradation, lap time, overtake, race result)
- **📦 Model Registry**: MinIO storage + PostgreSQL metadata with versioning
- **🔮 Predictions API**: 4 prediction endpoints with <1s latency
- **📊 Predictions UI**: Interactive page + dashboard integration cards
- **⚙️ Training Automation**: Async Celery tasks for model training

**Upcoming Phases**:
- **🎮 Strategy Simulator**: Undercut/overcut analysis, safety car decision support (Phase 2)
- **🤖 LLM Integration**: RAG-powered "race engineer" chatbot with citations (Phase 3)
- **📹 Computer Vision**: Pit stop timing, incident detection (Phase 4)
- **⚡ Live Streaming**: WebSocket-based live timing (Phase 5)

### 💡 Technical Highlights

- **Microservices Architecture**: Dockerized FastAPI + Next.js + Celery workers
- **Type-Safe Full Stack**: Python (mypy) + TypeScript (strict mode)
- **Production Patterns**: Feature store, model registry, async task queue
- **Professional Git Workflow**: Feature branching, conventional commits, CI/CD
- **Comprehensive Testing**: Unit + integration + E2E tests
- **Documentation-First**: ADRs, architecture diagrams, API docs

---

## 🛠️ Tech Stack

### Backend
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)

- **Framework**: FastAPI (async, high-performance REST API)
- **Database**: PostgreSQL 16 + pgvector (for embeddings)
- **ORM**: SQLAlchemy 2.0 + Alembic (migrations)
- **Task Queue**: Celery + Redis (distributed async processing)
- **Validation**: Pydantic v2 (type-safe schemas)
- **Package Manager**: uv (10-100x faster than pip)

### Machine Learning
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-CC0000?style=for-the-badge)
![LightGBM](https://img.shields.io/badge/LightGBM-00A7E1?style=for-the-badge)

- **Frameworks**: XGBoost (regression/classification), LightGBM (classification with class imbalance)
- **Feature Engineering**: scipy (linear regression), pandas (transformations)
- **Model Storage**: MinIO (S3-compatible) + joblib serialization
- **Model Registry**: PostgreSQL with metrics tracking and versioning

### Frontend
![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **Charts**: Recharts (declarative React charts)
- **State**: React hooks + Server Components

### Infrastructure & DevOps
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)

- **Development**: Docker Compose (6-service stack)
- **CI/CD**: GitHub Actions (lint → test → build)
- **Object Storage**: MinIO (S3-compatible)
- **Code Quality**: Ruff, Black, mypy, ESLint, Prettier

### Data Sources
- **FastF1**: Official F1 timing/telemetry data (pandas-based)
- **OpenF1**: Real-time API + live streaming
- **Jolpica**: Historical metadata (Ergast replacement)

---

## 📂 Project Structure

```
f1-analytics-lab/
├── apps/
│   ├── api/                # FastAPI backend + Celery workers
│   │   ├── src/f1hub/
│   │   │   ├── core/      # Config, logging, errors
│   │   │   ├── db/        # SQLAlchemy models (18 tables)
│   │   │   ├── api/       # FastAPI routes (v1/)
│   │   │   ├── schemas/   # Pydantic request/response models
│   │   │   ├── services/  # Business logic (ingestion, features, ML)
│   │   │   ├── ml/        # ML models & feature engineering (Phase 1)
│   │   │   │   ├── base.py           # BaseMLModel abstract class
│   │   │   │   ├── models/           # 4 trained models
│   │   │   │   │   ├── tyre_degradation.py
│   │   │   │   │   ├── lap_time.py
│   │   │   │   │   ├── overtake.py
│   │   │   │   │   └── race_result.py
│   │   │   │   └── features/         # Feature computation
│   │   │   │       ├── lap_features.py
│   │   │   │       ├── stint_features.py
│   │   │   │       └── battle_features.py
│   │   │   └── workers/   # Celery tasks (ingest, features, training)
│   │   ├── alembic/       # Database migrations
│   │   ├── tests/         # pytest unit + integration tests
│   │   └── Dockerfile
│   │
│   └── web/               # Next.js frontend
│       ├── src/
│       │   ├── app/       # Pages (App Router)
│       │   │   ├── dashboard/        # Main analytics dashboard
│       │   │   └── predictions/      # ML predictions UI (Phase 1)
│       │   ├── components/# React components
│       │   │   ├── charts/           # Recharts visualizations
│       │   │   ├── predictions/      # Prediction UI components
│       │   │   └── ui/               # Reusable UI elements
│       │   ├── lib/       # API client + utilities
│       │   └── types/     # TypeScript types
│       └── Dockerfile
│
├── libs/                  # Shared libraries (monorepo pattern)
│   └── f1data/           # Data clients + parsers (FastF1, OpenF1, Jolpica)
│
├── docs/                  # Documentation
│   ├── architecture.md   # System design + diagrams
│   ├── decisions.md      # Technical decision records (ADRs)
│   └── screenshots/      # Demo images
│
├── scripts/              # DevOps helper scripts
│   ├── dev_up.sh
│   ├── dev_down.sh
│   ├── seed_demo_data.py
│   ├── train_*.py        # Model training scripts (Phase 1)
│   └── test_*.sh         # Feature/prediction tests
│
├── .github/workflows/    # CI/CD pipelines
├── docker-compose.yml    # Multi-service orchestration (6 services)
├── Makefile             # Development commands
└── CHANGELOG.md         # Release history
```

**See [docs/architecture.md](docs/architecture.md) for detailed system design.**

## 🏗️ Project Phases

This project is built incrementally across 5 phases to demonstrate end-to-end development skills:

### Phase 0: Foundation (✅ COMPLETE - Q1 2025)
**Goal**: One-button workflow: select race → ingest → visualize

**Deliverables**:
- ✅ Docker Compose multi-service stack (6 services)
- ✅ PostgreSQL schema with migrations (18 tables)
- ✅ FastAPI with core endpoints (15+ routes)
- ✅ Celery async task queue
- ✅ FastF1 data ingestion pipeline
- ✅ Next.js dashboard with Recharts
- ✅ Feature tables (lap, stint, battle)

### Phase 1: ML Predictions (✅ COMPLETE - Q1 2025)
**Goal**: Train ML models and build predictions interface

**Deliverables**:
- ✅ Feature engineering (scipy linear regression for tyre deg)
- ✅ Tyre degradation model (LightGBM, RMSE 0.061 s/lap)
- ✅ Lap time forecasting (XGBoost, RMSE 0.638s, R² 0.757)
- ✅ Overtake probability (LightGBM classifier, ROC-AUC 0.741)
- ✅ Race result prediction (XGBoost regression, MAE 5.73 positions)
- ✅ Model registry & versioning (MinIO + PostgreSQL)
- ✅ Prediction API endpoints (4 models, <1s latency)
- ✅ Predictions UI page with interactive forms
- ✅ Dashboard integration (summary cards)
- ✅ Async training automation (Celery tasks)

### Phase 2: Strategy Simulator (Q3 2025)
- Race simulation engine
- Undercut/overcut predictor
- Safety car strategy recommender

### Phase 3: LLM/RAG (Q4 2025)
- RAG-powered chatbot with citations
- Post-race report generator
- Multi-depth explanations

### Phase 4: Computer Vision (Q1 2026)
- Pit stop timing from video
- Incident detection

### Phase 5: Live Streaming (Q2 2026)
- WebSocket real-time updates
- Rolling predictions

---

### Prerequisites

Before you begin, ensure you have:

- **Docker** & **Docker Compose** (required)
- **Git** (for version control)
- **Make** (optional, for convenience commands)

Optional for local development without Docker:
- Python 3.11+
- Node.js 20+

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/f1-analytics-lab.git
   cd f1-analytics-lab
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred text editor if needed
   ```

3. **Start all services**
   ```bash
   make dev-up
   # Or: bash scripts/dev_up.sh
   # Or: docker compose up --build
   ```

4. **Wait for services to be healthy** (30-60 seconds)
   - API will run migrations automatically
   - Check logs: `make dev-logs`

5. **Access the applications**
   - 🌐 **Web UI**: http://localhost:3000
   - 🚀 **API**: http://localhost:8000
   - 📚 **API Docs (Swagger)**: http://localhost:8000/docs
   - 🗂️ **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

6. **(Optional) Seed demo data**
   ```bash
   make db-seed
   # This will ingest 2024 Bahrain GP Race data
   ```

---

## 🤖 Using ML Predictions

Phase 1 adds machine learning capabilities for predicting race outcomes, lap times, and more.

### Training Models

Train all models from scratch:

```bash
# Train individual models
docker compose exec api python scripts/train_tyre_degradation.py
docker compose exec api python scripts/train_lap_time.py
docker compose exec api python scripts/train_overtake.py
docker compose exec api python scripts/train_race_result.py

# Or trigger async training via API
curl -X POST http://localhost:8000/api/v1/models/train \
  -H "Content-Type: application/json" \
  -d '{"model_name": "tyre_degradation"}'

# Check training status
curl http://localhost:8000/api/v1/models/train/{task_id}
```

### Making Predictions

#### Via API

```bash
# Tyre degradation (requires stint ID)
curl "http://localhost:8000/api/v1/predictions/tyre-degradation/{stint_id}"

# Lap time prediction
curl "http://localhost:8000/api/v1/predictions/lap-time?tyre_age=10&compound=SOFT&track_status=GREEN&position=5&driver_id=VER"

# Overtake probability
curl "http://localhost:8000/api/v1/predictions/overtake?gap_seconds=1.2&closing_rate=-0.1&tyre_advantage=1&drs_available=true&lap_number=30"

# Race result
curl "http://localhost:8000/api/v1/predictions/race-result?grid_position=3&avg_lap_time=92.5&driver_id=VER"
```

#### Via Web UI

1. Navigate to http://localhost:3000/predictions
2. Select a model from the available options
3. Fill in the prediction parameters
4. Click "Make Prediction" to see results

Predictions are also integrated into the dashboard as summary cards when viewing a session.

### Model Performance

| Model | Type | Metric | Value | Notes |
|-------|------|--------|-------|-------|
| Tyre Degradation | Regression | RMSE | 0.061 s/lap | Predicts degradation rate |
| Lap Time | Regression | RMSE | 0.638s | Good accuracy, R² 0.757 |
| Lap Time | Regression | R² | 0.757 | Explains 75.7% of variance |
| Overtake | Classification | ROC-AUC | 0.741 | Handles imbalanced data |
| Overtake | Classification | F1-Score | 0.571 | Balance precision/recall |
| Race Result | Regression | MAE | 5.73 positions | Needs more training data |
| Race Result | Regression | Within ±3 | 25% | Will improve with more races |

**Note**: Models are trained on 2024 Bahrain GP data. Performance will improve as more race sessions are ingested.

---

### Development Commands

All common operations are available via the Makefile:

```bash
make dev-up          # Start all services
make dev-down        # Stop all services
make dev-logs        # Tail logs
make dev-restart     # Restart services

make db-migrate      # Run database migrations
make db-seed         # Seed demo data
make db-shell        # Open PostgreSQL shell

make api-shell       # Open API container shell
make worker-shell    # Open worker container shell

make test-api        # Run API tests
make test-web        # Run frontend tests

make lint            # Lint all code
make format          # Format all code

make clean           # Remove all containers, volumes, caches
```

---

## 💻 Development Workflow

This project follows professional Git practices to showcase software engineering discipline:

### Branching Strategy

```
main           ← Production-ready code
  ↑
dev            ← Integration branch (all features merge here first)
  ↑
feature/*      ← Individual features
fix/*          ← Bug fixes
docs/*         ← Documentation updates
```

### Working on a New Feature

1. **Create a feature branch from `dev`**
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/your-feature-name
   ```

2. **Make small, focused commits**
   ```bash
   git add <files>
   git commit -m "feat: add lap time visualization component"
   ```

3. **Push and create a PR to `dev`**
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub targeting 'dev' branch
   ```

4. **After PR approval, merge to `dev`**
   ```bash
   git checkout dev
   git merge feature/your-feature-name
   git push origin dev
   ```

5. **Periodically, merge `dev` → `main` for releases**

### Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: bug fix
docs: documentation changes
test: add or update tests
refactor: code refactoring (no behavior change)
chore: tooling, config, dependencies
perf: performance improvements
ci: CI/CD pipeline changes
```

**Examples**:
- `feat: implement FastF1 data ingestion pipeline`
- `fix: handle null lap times in chart rendering`
- `docs: add architecture diagrams to docs/`
- `test: add unit tests for stint detection logic`
- `refactor: extract database session logic to util`

### Testing Before Commit

```bash
# Run linters
make lint

# Run tests
make test-api
make test-web

# Check types
docker compose exec api mypy src/
```

---

## 📊 Project Status

### Phase 0 Progress

- [x] Project structure and documentation
- [x] Git branching strategy
- [x] Docker Compose configuration
- [ ] Database schema and migrations
- [ ] FastAPI core endpoints
- [ ] Celery worker setup
- [ ] FastF1 ingestion service
- [ ] Next.js frontend skeleton
- [ ] Recharts visualization
- [ ] CI/CD pipelines

**Current Milestone**: Week 1 - Infrastructure & Database

See [CHANGELOG.md](CHANGELOG.md) for detailed release notes.

---

## 🧪 Testing

### Backend (pytest)
```bash
# Run all tests
make test-api

# Run specific test file
docker compose exec api pytest tests/test_services/test_fastf1_ingest.py

# Run with coverage
docker compose exec api pytest --cov=f1hub --cov-report=html
```

### Frontend (Jest + React Testing Library)
```bash
# Run all tests
make test-web

# Watch mode
docker compose exec web npm test -- --watch
```

### Integration Tests
```bash
# Full end-to-end ingestion test
docker compose exec api pytest tests/integration/test_full_ingestion.py -v
```

---

## 📖 Documentation

- **[Architecture](docs/architecture.md)**: System design, data flow, tech stack details
- **[Technical Decisions](docs/decisions.md)**: ADRs explaining key architectural choices
- **[CHANGELOG](CHANGELOG.md)**: Release history and planned features
- **[API Docs](http://localhost:8000/docs)**: Interactive Swagger documentation (when running)

---

## 🤝 Contributing

This is a solo portfolio project, but suggestions are welcome!

### How to Suggest Improvements

1. Open an issue describing your idea
2. If it aligns with the project goals, I may implement it
3. PRs are welcome for bug fixes or documentation improvements

### Code Standards

- **Python**: Ruff + Black + mypy (strict mode)
- **TypeScript**: ESLint + Prettier (strict mode)
- **Commits**: Conventional Commits format
- **Tests**: Required for new features
- **Documentation**: Update docs/ when changing architecture

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[FastF1](https://github.com/theOehrly/Fast-F1)**: Excellent F1 telemetry library
- **[OpenF1](https://openf1.org/)**: Real-time F1 API
- **[Jolpica](https://github.com/jolpica/jolpica-f1)**: Ergast API replacement

---

## 📧 Contact

**Ansh** - [Your LinkedIn](https://linkedin.com/in/yourprofile) | [Your Portfolio](https://yourwebsite.com)

Built with ❤️ to showcase full-stack development, data engineering, and ML engineering skills.

---

**⭐ If you found this project helpful, please consider starring the repository!**
