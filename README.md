# SupportMind

SupportMind — это full-stack ML-проект для анализа обращений пользователей.

Приложение принимает текст тикета, определяет:
- категорию обращения
- приоритет
- тональность

Также система:
- сохраняет результаты в PostgreSQL
- показывает историю анализов
- позволяет работать через REST API
- запускается через Docker Compose

---

## Стек технологий

### Backend
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- PostgreSQL

### ML / NLP
- pandas
- numpy
- scikit-learn
- joblib

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS

### Infra
- Docker
- Docker Compose

---

## Структура проекта

```text
supportmind/
├─ backend/
├─ frontend/
├─ docs/
├─ docker-compose.yml
├─ .gitignore
└─ README.md