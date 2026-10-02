from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str
    password: str


class UserPublic(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class VideoPublic(BaseModel):
    id: int
    title: str
    description: str
    video_url: str
    thumbnail_url: str | None
    views: int
    user_id: int
    user_name: str
    created_at: datetime


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentPublic(BaseModel):
    id: int
    content: str
    user_id: int
    user_name: str
    created_at: datetime
