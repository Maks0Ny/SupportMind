# Quality And CI

SupportMind uses automated checks to keep backend, frontend, Docker, and tests healthy.

---

## Local Checks

Backend:

```powershell
cd backend
python -m pytest
python -m pytest --cov=app --cov-report=term-missing
python -m ruff check app tests
python -m ruff format --check app tests
```

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

Docker:

```powershell
docker build -t supportmind-backend:test ./backend
docker build --build-arg VITE_API_BASE_URL=http://localhost:8000/api/v1 -t supportmind-frontend:test ./frontend
```

Makefile shortcuts:

```bash
make test-backend
make test-frontend
make lint-backend
make build-frontend
```

---

## GitHub Actions

Workflows:

```text
.github/workflows/backend-ci.yml
.github/workflows/frontend-ci.yml
.github/workflows/docker-ci.yml
```

They run on pushes and pull requests targeting `main`.

Backend CI checks:

- install dependencies;
- Ruff lint;
- Ruff format check;
- pytest;
- coverage threshold.

Frontend CI checks:

- `npm ci`;
- ESLint;
- production build.

Docker CI checks:

- backend image build;
- frontend image build.

---

## Tests

Backend tests use SQLite fixtures instead of the real PostgreSQL database.

Redis cache calls are mocked where needed so tests stay fast and isolated.

The ML production predictor has fallback behavior: if model artifacts are unavailable in CI, the backend can still import and run using the rule-based predictor.

---

## ML Quality Artifacts

Training creates:

```text
backend/ml/artifacts/metrics.json
backend/ml/artifacts/training_history.json
backend/ml/artifacts/training_history.png
backend/ml/artifacts/final_metrics.png
backend/ml/artifacts/confusion_matrix.png
```

Use these files to inspect:

- train vs validation loss;
- train vs validation F1;
- final accuracy, precision, recall, F1;
- category confusion matrix.

These files are local artifacts and are not committed to Git.

---

## Dependency Split

Runtime backend dependencies are in:

```text
backend/requirements.txt
```

ML training dependencies are in:

```text
backend/requirements-ml.txt
```

The backend runtime currently includes `torch` and `transformers` because the API can load the trained predictor. Training-only tools such as `pandas`, `scikit-learn`, `matplotlib`, and `seaborn` stay in `requirements-ml.txt`.

---

## Recommended Before Push

Run:

```powershell
cd backend
python -m ruff check app tests
python -m pytest
```

Then:

```powershell
cd ..\frontend
npm run lint
npm run build
```

Finally:

```powershell
docker compose build
```
