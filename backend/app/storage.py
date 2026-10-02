import os
import uuid
from pathlib import Path

import boto3
from fastapi import HTTPException, UploadFile

from .config import settings

VIDEO_TYPES = {"video/mp4"}
IMAGE_TYPES = {"image/jpeg", "image/png"}


def _s3_enabled(bucket: str) -> bool:
    return bool(bucket)


def _public_url(bucket: str, key: str) -> str:
    if settings.s3_public_base_url:
        return f"{settings.s3_public_base_url.rstrip('/')}/{key}"
    client = boto3.client("s3", region_name=settings.aws_region)
    return client.generate_presigned_url("get_object", Params={"Bucket": bucket, "Key": key}, ExpiresIn=86400)


def get_upload_url(key: str | None, kind: str) -> str | None:
    if not key:
        return None
    bucket = settings.s3_video_bucket if kind == "video" else settings.s3_thumbnail_bucket
    if _s3_enabled(bucket):
        return _public_url(bucket, key)
    folder = "videos" if kind == "video" else "thumbnails"
    return f"/uploads/{folder}/{os.path.basename(key)}"


async def save_upload(upload: UploadFile, kind: str) -> tuple[str, str]:
    is_video = kind == "video"
    allowed = VIDEO_TYPES if is_video else IMAGE_TYPES
    max_bytes = (settings.max_video_mb if is_video else settings.max_image_mb) * 1024 * 1024
    bucket = settings.s3_video_bucket if is_video else settings.s3_thumbnail_bucket
    extension = Path(upload.filename or "").suffix.lower()
    valid_extensions = {".mp4"} if is_video else {".jpg", ".jpeg", ".png"}
    if upload.content_type not in allowed or extension not in valid_extensions:
        raise HTTPException(status_code=415, detail="Formato de archivo no permitido")

    data = await upload.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail=f"El archivo supera el límite de {max_bytes // (1024 * 1024)} MB")
    key = f"{uuid.uuid4().hex}{extension}"

    if _s3_enabled(bucket):
        client = boto3.client("s3", region_name=settings.aws_region)
        client.put_object(Bucket=bucket, Key=key, Body=data, ContentType=upload.content_type)
        url = f"s3://{bucket}/{key}"
    else:
        directory = Path(settings.upload_dir) / ("videos" if is_video else "thumbnails")
        directory.mkdir(parents=True, exist_ok=True)
        (directory / key).write_bytes(data)
        url = f"/uploads/{'videos' if is_video else 'thumbnails'}/{key}"
    return key, url


def delete_upload(key: str | None, kind: str) -> None:
    if not key:
        return
    bucket = settings.s3_video_bucket if kind == "video" else settings.s3_thumbnail_bucket
    if _s3_enabled(bucket):
        boto3.client("s3", region_name=settings.aws_region).delete_object(Bucket=bucket, Key=key)
        return
    directory = Path(settings.upload_dir) / ("videos" if kind == "video" else "thumbnails")
    path = directory / os.path.basename(key)
    path.unlink(missing_ok=True)
