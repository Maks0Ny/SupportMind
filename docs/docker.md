# Docker Guide

Docker Compose starts the full SupportMind stack:

- PostgreSQL
- Redis
- FastAPI backend
- React frontend served by Nginx

---

## Run

From the project root:

```powershell
docker compose up --build
```

Detached mode:

```powershell
docker compose up -d --build
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

## URLs

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000
Swagger:  http://localhost:8000/docs
Database: localhost:5433
Redis:    localhost:6379
```

---

## Services

```text
db       postgres:16
redis    redis:7-alpine
backend  FastAPI + Uvicorn
frontend Nginx static frontend
```

The backend waits for PostgreSQL and Redis healthchecks, runs Alembic migrations, and then starts Uvicorn.

---

## Backend Environment

Inside Docker:

```env
POSTGRES_HOST=db
POSTGRES_PORT=5432
REDIS_HOST=redis
REDIS_PORT=6379
ML_USE_TRAINED_MODEL=true
ML_DEVICE=cpu
```

On the host machine:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## ML In Docker

The backend image installs `torch` and `transformers` because the API can load the trained category model.

The model artifacts are expected at:

```text
backend/ml/artifacts/category_model.pt
backend/ml/artifacts/label_mapping.json
```

If artifacts exist during local Docker build, they are copied into the backend image by `COPY . .`.

If artifacts are missing, the backend falls back to rule-based prediction and keeps running.

For Docker CPU inference:

```env
ML_DEVICE=cpu
```

For CUDA inference, a normal `python:3.12-slim` Docker image is not enough. You would need an NVIDIA-enabled runtime and a CUDA-compatible image. Keep Docker inference on CPU for this project stage.

---

## Logs

All logs:

```powershell
docker compose logs
```

Backend logs:

```powershell
docker compose logs -f backend
```

Redis check:

```powershell
docker exec -it supportmind_redis redis-cli
```

Inside Redis:

```redis
KEYS *
GET dashboard:summary
```

---

## Reset Local Data

Remove containers and PostgreSQL volume:

```powershell
docker compose down -v
docker compose up --build
```

Use this only when you are fine with deleting local database data.

---

## Common Issues

### Backend Connects To `localhost`

Inside Docker, backend must use:

```env
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

`localhost` inside a container means the container itself.

### Frontend Cannot Reach API

The frontend build arg must include `/api/v1`:

```text
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Docker Image Is Large

The backend image is larger after ML integration because `torch`, `transformers`, and model weights are heavy.

For a production portfolio improvement, model artifacts can later be stored outside the image and downloaded or mounted at runtime.
