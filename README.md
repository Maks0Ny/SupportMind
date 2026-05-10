# SupportMind

[![Backend CI](https://github.com/Maks0Ny/SupportMind/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/Maks0Ny/SupportMind/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/Maks0Ny/SupportMind/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/Maks0Ny/SupportMind/actions/workflows/frontend-ci.yml)
[![Docker CI](https://github.com/Maks0Ny/SupportMind/actions/workflows/docker-ci.yml/badge.svg)](https://github.com/Maks0Ny/SupportMind/actions/workflows/docker-ci.yml)

SupportMind is a full-stack support ticket analysis platform. It combines a FastAPI backend, React frontend, PostgreSQL storage, Redis caching, Docker infrastructure, and a trained ML category classifier.

The application accepts support ticket text, predicts category, priority, sentiment, and confidence, stores ticket history, allows manual prediction editing, provides filters, and displays dashboard analytics.

---

## Features

- FastAPI REST API with versioned routes
- React + TypeScript frontend
- PostgreSQL persistence with SQLAlchemy
- Alembic database migrations
- Redis cache for dashboard summary
- Request logging middleware with `X-Request-ID`
- Service layer for business logic
- Trained PyTorch/Transformers category classifier
- Rule-based fallback predictor for safe local startup
- Rule-based priority and sentiment detection
- Dataset preprocessing, train/validation/test split, training, inference, evaluation, losses, and visualizations
- Docker Compose local environment
- GitHub Actions for backend, frontend, and Docker checks

---

## Tech Stack

Backend:

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- PyTorch
- Transformers
- pytest
- Ruff

Frontend:

- React
- TypeScript
- Vite
- ESLint

Infrastructure:

- Docker
- Docker Compose
- Nginx
- GitHub Actions
- PowerShell startup script
- Makefile shortcuts

---

## Project Structure

```text
supportmind/
├─ backend/
│  ├─ app/
│  │  ├─ api/
│  │  ├─ core/
│  │  ├─ db/
│  │  ├─ middleware/
│  │  ├─ ml/
│  │  ├─ models/
│  │  ├─ schemas/
│  │  ├─ services/
│  │  └─ main.py
│  ├─ alembic/
│  ├─ ml/
│  │  ├─ artifacts/
│  │  ├─ configs/
│  │  ├─ data/
│  │  └─ training/
│  ├─ tests/
│  ├─ requirements.txt
│  ├─ requirements-ml.txt
│  └─ Dockerfile
├─ frontend/
│  ├─ src/
│  ├─ Dockerfile
│  └─ nginx.conf
├─ docs/
├─ scripts/
├─ .github/workflows/
├─ docker-compose.yml
├─ Makefile
└─ README.md
```

---

## Quick Start

From the project root:

```powershell
cd J:\VScode_Projects\supportmind
docker compose up --build
```

Open:

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000
Swagger:  http://localhost:8000/docs
```

Stop:

```powershell
docker compose down
```

Clean rebuild:

```powershell
docker compose down
docker compose build --no-cache
docker compose up
```

---

## Startup Helpers

PowerShell:

```powershell
.\scripts\start-local.ps1
.\scripts\start-local.ps1 -Mode native
```

Makefile, if `make` is installed:

```bash
make docker
make native
make stop
make test-backend
make test-frontend
```

---

## API

Base URL:

```text
http://localhost:8000/api/v1
```

Main endpoints:

```http
GET    /health
POST   /tickets/analyze
GET    /tickets
GET    /tickets/{ticket_id}
PUT    /tickets/{ticket_id}/prediction
DELETE /tickets/{ticket_id}
GET    /dashboard/summary
```

More details: [docs/api.md](docs/api.md).

---

## ML Workflow

Raw datasets are stored locally in:

```text
backend/ml/data/raw/
```

Generated datasets are stored locally in:

```text
backend/ml/data/processed/
```

Model artifacts are stored locally in:

```text
backend/ml/artifacts/
```

These folders are ignored by Git because datasets and model weights are large.

Prepare data:

```powershell
cd backend
pip install -r requirements-ml.txt
python ml\training\preprocess_dataset.py
python ml\training\prepare_dataset.py
```

Train model:

```powershell
python ml\training\train.py
```

Run local inference check:

```powershell
python ml\training\inferences.py "I cannot login to my account" --device cpu
```

Production API behavior:

- if `backend/ml/artifacts/category_model.pt` and `label_mapping.json` exist, the API uses the trained model for `category`;
- if artifacts are missing or ML loading fails, the API falls back to the rule-based category predictor;
- `priority` and `sentiment` are still calculated with rule-based logic.

---

## Environment

Backend variables:

```env
APP_NAME=SupportMind
APP_ENV=development
APP_DEBUG=true
API_V1_PREFIX=/api/v1
LOG_LEVEL=INFO

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=supportmind
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL_SECONDS=60

ML_USE_TRAINED_MODEL=true
ML_DEVICE=cpu
```

Use `ML_DEVICE=cuda` only when PyTorch can see your NVIDIA GPU.

---

## Tests And Checks

Backend:

```powershell
cd backend
python -m pytest
python -m ruff check app tests
python -m ruff format --check app tests
```

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

More details: [docs/quality.md](docs/quality.md).

---

## Documentation

- [Architecture](docs/architecture.md)
- [API](docs/api.md)
- [Docker](docs/docker.md)
- [Local development](docs/local-development.md)
- [Database migrations](docs/database-migrations.md)
- [Quality and CI](docs/quality.md)

---

