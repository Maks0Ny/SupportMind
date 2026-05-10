.PHONY: help docker native stop backend frontend test-backend test-frontend lint-backend build-frontend

help:
	@echo "SupportMind commands:"
	@echo "  make docker          Start full project with Docker Compose"
	@echo "  make native          Start backend and frontend locally through PowerShell"
	@echo "  make stop            Stop Docker Compose services"
	@echo "  make backend         Start backend locally"
	@echo "  make frontend        Start frontend locally"
	@echo "  make test-backend    Run backend tests"
	@echo "  make test-frontend   Run frontend checks"
	@echo "  make lint-backend    Run backend Ruff checks"
	@echo "  make build-frontend  Build frontend"

docker:
	powershell -ExecutionPolicy Bypass -File scripts/start-local.ps1 -Mode docker

native:
	powershell -ExecutionPolicy Bypass -File scripts/start-local.ps1 -Mode native

stop:
	docker compose down

backend:
	cd backend && ../venv/Scripts/python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

frontend:
	cd frontend && npm run dev

test-backend:
	cd backend && ../venv/Scripts/python.exe -m pytest

test-frontend:
	cd frontend && npm run lint && npm run build

lint-backend:
	cd backend && ../venv/Scripts/python.exe -m ruff check app tests

build-frontend:
	cd frontend && npm run build
