import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User, Video
from ..schemas import LoginRequest, UserCreate, UserPublic
from ..security import create_token, hash_password, verify_password
from ..storage import get_upload_url

router = APIRouter(tags=["Usuarios"])


def account_response(user: User) -> dict:
    return {"access_token": create_token(user.id), "token_type": "bearer", "user": UserPublic.model_validate(user).model_dump()}


@router.post("/users", status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise HTTPException(status_code=422, detail="Introduce un correo válido")
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status_code=409, detail="Ya existe una cuenta con ese correo")
    user = User(name=payload.name.strip(), email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return account_response(user)


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email.strip().lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    return account_response(user)


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db), _current: User = Depends(get_current_user)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    videos = db.scalars(select(Video).where(Video.user_id == user.id).order_by(Video.created_at.desc())).all()
    return {
        **UserPublic.model_validate(user).model_dump(),
        "video_count": len(videos),
        "videos": [
            {"id": video.id, "title": video.title, "description": video.description,
             "video_url": get_upload_url(video.video_key, "video"),
             "thumbnail_url": get_upload_url(video.thumbnail_key, "thumbnail"), "views": video.views, "user_id": video.user_id,
             "user_name": user.name, "created_at": video.created_at}
            for video in videos
        ],
    }
