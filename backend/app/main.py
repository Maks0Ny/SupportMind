from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.endpoints.tickets import router as tickets_router


app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.APP_DEBUG,
)

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


@app.get("/")
def root():
    return {"message": f"{settings.APP_NAME} is running"}


@app.get(f"{settings.API_V1_PREFIX}/health")
def health():
    return {"status": "ok"}