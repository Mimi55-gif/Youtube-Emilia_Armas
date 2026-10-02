from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User, Video
from ..schemas import VideoPublic
from ..storage import delete_upload, get_upload_url, save_upload

router = APIRouter(prefix="/videos", tags=["Videos"])


def serialize_video(video: Video) -> dict:
    return {
        "id": video.id, "title": video.title, "description": video.description,
        "video_url": get_upload_url(video.video_key, "video"),
        "thumbnail_url": get_upload_url(video.thumbnail_key, "thumbnail"),
        "views": video.views, "user_id": video.user_id, "user_name": video.owner.name,
        "created_at": video.created_at,
    }


@router.get("")
def list_videos(db: Session = Depends(get_db)):
    videos = db.scalars(select(Video).options(joinedload(Video.owner)).order_by(Video.created_at.desc())).all()
    return [serialize_video(video) for video in videos]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_video(
    title: str = Form(min_length=2, max_length=140),
    description: str = Form(default="", max_length=5000),
    video_file: UploadFile = File(...),
    thumbnail_file: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    video_key, video_url = await save_upload(video_file, "video")
    thumbnail_key = thumbnail_url = None
    try:
        if thumbnail_file and thumbnail_file.filename:
            thumbnail_key, thumbnail_url = await save_upload(thumbnail_file, "thumbnail")
        video = Video(
            title=title.strip(), description=description.strip(), video_url=video_url,
            video_key=video_key, thumbnail_url=thumbnail_url, thumbnail_key=thumbnail_key,
            owner=user,
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        return serialize_video(video)
    except Exception:
        delete_upload(video_key, "video")
        delete_upload(thumbnail_key, "thumbnail")
        raise


@router.get("/{video_id}")
def get_video(video_id: int, db: Session = Depends(get_db)):
    video = db.scalar(select(Video).options(joinedload(Video.owner)).where(Video.id == video_id))
    if video is None:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    video.views += 1
    db.commit()
    db.refresh(video)
    return serialize_video(video)


@router.get("/{video_id}/recommendations")
def recommendations(video_id: int, db: Session = Depends(get_db)):
    current = db.get(Video, video_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    videos = db.scalars(
        select(Video).options(joinedload(Video.owner)).where(Video.id != video_id)
        .order_by(Video.user_id == current.user_id, Video.views.desc(), Video.created_at.desc()).limit(6)
    ).all()
    return [serialize_video(video) for video in videos]


@router.put("/{video_id}")
def update_video(
    video_id: int,
    title: str = Form(min_length=2, max_length=140),
    description: str = Form(default="", max_length=5000),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    video = db.get(Video, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    if video.user_id != user.id:
        raise HTTPException(status_code=403, detail="Solo puedes editar tus videos")
    video.title = title.strip()
    video.description = description.strip()
    db.commit()
    db.refresh(video)
    return serialize_video(video)


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_video(video_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    video = db.get(Video, video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    if video.user_id != user.id:
        raise HTTPException(status_code=403, detail="Solo puedes eliminar tus videos")
    delete_upload(video.video_key, "video")
    delete_upload(video.thumbnail_key, "thumbnail")
    db.delete(video)
    db.commit()
