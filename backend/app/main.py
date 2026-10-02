from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from . import models
from .config import settings
from .database import Base, engine
from .routes.comments import router as comments_router
from .routes.users import router as users_router
from .routes.videos import router as videos_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mimi API",
    description="API para la plataforma de videos Mimi",
    version="1.0.0",
)

# Lista de orígenes para CORS
origins = (
    settings.allowed_origins
    if isinstance(settings.allowed_origins, list)
    else [settings.allowed_origins]
)
s3_origin = "http://emilia-frontend-videos-app.s3-website-us-east-1.amazonaws.com"
if s3_origin not in origins:
    origins.append(s3_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Manejador global de excepciones para mantener las cabeceras CORS en errores 500
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Error interno en el servidor: {str(exc)}"},
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

