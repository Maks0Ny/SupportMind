# Architecture

SupportMind is a full-stack ticket analysis system with a React frontend, FastAPI backend, PostgreSQL database, Redis cache, and ML inference layer.

---

## High-Level Flow

```text
User
  ↓
React Frontend
  ↓ HTTP
FastAPI API Layer
  ↓
Service Layer
  ├─ PostgreSQL through SQLAlchemy
  ├─ Redis dashboard cache
  └─ ML predictor
```

---

## Backend Layers

```text
backend/app/
├─ api/          FastAPI routers and API dependencies
├─ core/         settings, logging, Redis client
├─ db/           SQLAlchemy engine and sessions
├─ middleware/   request logging middleware
├─ ml/           production predictor interface
├─ models/       SQLAlchemy models
├─ schemas/      Pydantic request and response models
├─ services/     business logic
└─ main.py       application factory entrypoint
```

The API endpoints stay thin. They validate HTTP input, call services, and return Pydantic responses.

The service layer owns business behavior: ticket creation, prediction persistence, filters, deletion, dashboard aggregation, and cache invalidation.

---

## Frontend Layers

```text
frontend/src/
├─ api/          HTTP clients
├─ components/   UI components
├─ types/        TypeScript contracts
├─ App.tsx       main UI composition
└─ main.tsx      Vite entrypoint
```

The frontend communicates only with the backend API. It does not know whether prediction came from a trained model or fallback logic.

---

## Prediction Flow

```text
POST /api/v1/tickets/analyze
  ↓
ticket_service.analyze_ticket_service
  ↓
app.ml.category_predictor.predictor.predict(text)
  ↓
trained model for category, if artifacts are available
  ↓
rule-based fallback for category when ML is unavailable
  ↓
rule-based priority and sentiment
  ↓
prediction is stored in PostgreSQL
  ↓
dashboard cache is invalidated
```

Production API output stays stable:

```text
category
priority
sentiment
confidence
```

---

## ML Architecture

Production inference lives in:

```text
backend/app/ml/
├─ category_predictor.py
├─ trained_predictor.py
├─ model.py
└─ text_preprocessing.py
```

Training and experiments live in:

```text
backend/ml/
├─ artifacts/
├─ configs/
├─ data/
└─ training/
```

Important training modules:

- `preprocess_dataset.py` prepares the raw CSV.
- `prepare_dataset.py` creates train, validation, and test splits.
- `text_dataset.py` wraps data for PyTorch.
- `modeling.py` defines the model architecture.
- `train.py` runs training.
- `evaluation.py` calculates metrics.
- `losses.py` contains loss helpers.
- `visualization.py` saves training charts.
- `inferences.py` runs local model checks outside the API.

---

## ML Artifacts

Training produces:

```text
backend/ml/artifacts/category_model.pt
backend/ml/artifacts/label_mapping.json
backend/ml/artifacts/metrics.json
backend/ml/artifacts/training_history.json
backend/ml/artifacts/training_history.png
backend/ml/artifacts/final_metrics.png
backend/ml/artifacts/confusion_matrix.png
```

Artifacts are ignored by Git. A local Docker build can include them if they exist in the build context, but a fresh GitHub clone will not contain them.

---

## Cache Flow

`GET /dashboard/summary` uses Redis:

```text
dashboard service
  ↓
check Redis key dashboard:summary
  ↓
cache hit: return cached response
  ↓
cache miss: query PostgreSQL, store result, return response
```

Cache is cleared after:

- ticket creation;
- prediction update;
- ticket deletion.

---

## Database

Current tables:

```text
tickets
predictions
alembic_version
```

Relationship:

```text
tickets.id -> predictions.ticket_id
```

One ticket has one prediction.

---

## Observability

The backend adds `X-Request-ID` to responses and logs method, path, status code, duration, and request ID.

This helps connect frontend requests, API responses, and backend logs.

---

## Design Principles

- Keep API routes thin.
- Keep business logic in services.
- Keep model training outside production API code.
- Keep production predictor behind a stable interface.
- Use Redis only as an optimization, not as a source of truth.
- Use Alembic for schema changes.
- Keep large datasets and model artifacts out of Git.
