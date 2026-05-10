# Database Migrations

SupportMind uses Alembic to manage PostgreSQL schema changes.

---

## Why Alembic

Alembic gives the project:

- explicit schema history;
- repeatable local and Docker setup;
- reviewable migration files;
- safe upgrades and downgrades;
- no hidden table creation on application startup.

Do not use this in the application runtime:

```python
Base.metadata.create_all(bind=engine)
```

Tests may still create temporary tables in isolated test databases.

---

## Current Schema

Tables:

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

## Structure

```text
backend/
├─ alembic/
│  ├─ versions/
│  ├─ env.py
│  └─ script.py.mako
└─ alembic.ini
```

`alembic/env.py` imports application settings and uses the same database URL as the backend.

This matters in Docker: migrations connect to `db:5432`, not `localhost`.

---

## Commands

Run from `backend/`.

Apply migrations:

```powershell
alembic upgrade head
```

Create migration:

```powershell
alembic revision --autogenerate -m "describe change"
```

Rollback one migration:

```powershell
alembic downgrade -1
```

Show current revision:

```powershell
alembic current
```

Show history:

```powershell
alembic history
```

---

## Typical Workflow

1. Change SQLAlchemy models.
2. Generate migration.
3. Review generated migration file.
4. Apply migration locally.
5. Run tests.
6. Commit model and migration together.

Example:

```powershell
alembic revision --autogenerate -m "add updated_at to tickets"
alembic upgrade head
python -m pytest
```

---

## Docker

The backend container runs:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

This means the schema is upgraded before the API starts.

---

## Common Issues

### Empty Migration

Cause: Alembic cannot see SQLAlchemy models.

Check:

- models are imported in `alembic/env.py`;
- `target_metadata = Base.metadata`;
- command is run from `backend/`.

### Wrong Database Host

Local host machine:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
```

Docker backend container:

```env
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### Reset Development Database

Docker reset:

```powershell
docker compose down -v
docker compose up --build
```

This deletes local PostgreSQL data.
