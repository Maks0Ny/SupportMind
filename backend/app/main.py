from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.v1.endpoints.tickets import router as tickets_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.middleware.logging import log_requests_middleware


setup_logging(settings.LOG_LEVEL)

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.APP_DEBUG,
)

app.middleware("http")(log_requests_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tickets_router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} is running"}


@app.get(f"{settings.API_V1_PREFIX}/health")
def health():
    return {"status": "ok"}
