from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import Base, engine
from . import models
from .routes.comments import router as comments_router
from .routes.users import router as users_router
from .routes.videos import router as videos_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mimi API", description="API para la plataforma de videos Mimi", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_path = Path(settings.upload_dir)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_path), name="uploads")
app.include_router(users_router)
app.include_router(videos_router)
app.include_router(comments_router)


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
