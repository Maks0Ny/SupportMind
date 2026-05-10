# Local Development Guide

This guide explains how to run SupportMind on Windows with VS Code.

Docker Compose is the recommended path. Native local mode is useful when you want separate backend and frontend processes.

---

## Requirements

- Python 3.12+
- Node.js 20+
- Docker Desktop
- Git
- VS Code

Recommended extensions:

- Python
- Pylance
- Ruff
- ESLint
- Docker
- GitLens

---

## One-Command Startup

Docker mode:

```powershell
.\scripts\start-local.ps1
```

Native mode:

```powershell
.\scripts\start-local.ps1 -Mode native
```

Makefile shortcuts, if `make` is installed:

```bash
make docker
make native
make stop
```

---

## Backend Setup

```powershell
cd backend
python -m venv ..\venv
..\venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
APP_NAME=SupportMind
APP_ENV=development
APP_DEBUG=true
API_V1_PREFIX=/api/v1
LOG_LEVEL=INFO

POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=supportmind
POSTGRES_HOST=localhost
POSTGRES_PORT=5433

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL_SECONDS=60

ML_USE_TRAINED_MODEL=true
ML_DEVICE=cpu
```

Run migrations and backend:

```powershell
alembic upgrade head
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

```powershell
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Run frontend:

```powershell
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

## ML Dataset And Training

Install training dependencies:

```powershell
cd backend
pip install -r requirements-ml.txt
```

Place raw dataset:

```text
backend/ml/data/raw/dataset-tickets-multi-lang-4-20k.csv
```

Prepare dataset:

```powershell
python ml\training\preprocess_dataset.py
python ml\training\prepare_dataset.py
```

Train:

```powershell
python ml\training\train.py
```

Check inference:

```powershell
python ml\training\inferences.py "I cannot login to my account" --device cpu
```

Generated artifacts:

```text
backend/ml/artifacts/category_model.pt
backend/ml/artifacts/label_mapping.json
backend/ml/artifacts/metrics.json
backend/ml/artifacts/training_history.png
backend/ml/artifacts/final_metrics.png
backend/ml/artifacts/confusion_matrix.png
```

---

## Manual Test

Open:

```text
http://localhost:5173
```

Try:

```text
I cannot login to my account after password reset
```

Expected:

- ticket is created;
- prediction is displayed;
- ticket appears in history;
- dashboard updates;
- backend response includes `X-Request-ID`;
- dashboard summary is cached in Redis.

---

## Useful Commands

Backend tests:

```powershell
cd backend
python -m pytest
```

Backend lint:

```powershell
python -m ruff check app tests
```

Frontend checks:

```powershell
cd frontend
npm run lint
npm run build
```

Docker:

```powershell
docker compose up --build
docker compose down
```

---

## Common Issues

### PowerShell Blocks Script Execution

Use:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-local.ps1
```

### Backend Cannot Connect To PostgreSQL

Check `.env`:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
```

For Docker Compose, use:

```env
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### ML Model Does Not Load

Check:

```text
backend/ml/artifacts/category_model.pt
backend/ml/artifacts/label_mapping.json
```

If they are missing, the API uses fallback prediction.

### CUDA Does Not Work

Check:

```powershell
python -c "import torch; print(torch.cuda.is_available())"
```

If it prints `False`, install CUDA-enabled PyTorch and verify your NVIDIA driver.
