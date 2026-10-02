from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..dependencies import get_current_user
from ..models import Comment, User, Video
from ..schemas import CommentCreate

router = APIRouter(prefix="/videos/{video_id}/comments", tags=["Comentarios"])


@router.get("")
def list_comments(video_id: int, db: Session = Depends(get_db)):
    if db.get(Video, video_id) is None:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    comments = db.scalars(
        select(Comment).options(joinedload(Comment.author)).where(Comment.video_id == video_id)
        .order_by(Comment.created_at.desc())
    ).all()
    return [
        {"id": item.id, "content": item.content, "user_id": item.user_id,
         "user_name": item.author.name, "created_at": item.created_at}
        for item in comments
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
def add_comment(
    video_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if db.get(Video, video_id) is None:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    comment = Comment(content=payload.content.strip(), video_id=video_id, author=user)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {"id": comment.id, "content": comment.content, "user_id": user.id, "user_name": user.name, "created_at": comment.created_at}
