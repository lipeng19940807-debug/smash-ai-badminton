"""
视频相关 API 路由
"""
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from supabase import Client
from app.database import get_db
from app.models.video import VideoUploadResponse, Video, CloudVideoUploadRequest
from app.services.video_service import VideoService
from app.dependencies import get_current_user


router = APIRouter(prefix="/video", tags=["视频"])


@router.post("/upload", response_model=VideoUploadResponse, summary="上传视频")
# ... (原有逻辑) ...

@router.post("/cloud-upload", response_model=VideoUploadResponse, summary="同步云存储视频")
async def cloud_upload_video(
    request: CloudVideoUploadRequest,
    current_user: dict = Depends(get_current_user),
    db: Client = Depends(get_db)
):
    """
    同步小程序已上传到云存储的视频
    
    - **file_id**: 微信云存储 fileID
    """
    video_service = VideoService(db)
    result = await video_service.sync_cloud_video(
        file_id=request.file_id,
        user_id=current_user["id"],
        trim_start=request.trim_start,
        trim_end=request.trim_end
    )
    return result
async def upload_video(
    file: UploadFile = File(..., description="视频文件"),
    trim_start: Optional[float] = Form(None, description="裁剪起始时间(秒)"),
    trim_end: Optional[float] = Form(None, description="裁剪结束时间(秒)"),
    current_user: dict = Depends(get_current_user),
    db: Client = Depends(get_db)
):
    """
    上传视频文件
    
    - **file**: 视频文件 (MP4/MOV/AVI/MKV/WEBM，最大50MB)
    - **trim_start**: 可选，裁剪起始时间(秒)
    - **trim_end**: 可选，裁剪结束时间(秒)
    
    返回视频信息，包括处理后的文件路径和缩略图
    """
    video_service = VideoService(db)
    result = await video_service.upload_video(
        file=file,
        user_id=current_user["id"],
        trim_start=trim_start,
        trim_end=trim_end
    )
    return result


@router.get("/{video_id}", response_model=Video, summary="获取视频信息")
async def get_video(
    video_id: str,
    current_user: dict = Depends(get_current_user),
    db: Client = Depends(get_db)
):
    """
    获取视频信息
    
    - **video_id**: 视频ID
    
    返回视频的详细信息
    """
    video_service = VideoService(db)
    video = await video_service.get_video(video_id, current_user["id"])
    
    return {
        "id": video["id"],
        "original_filename": video["original_filename"],
        "duration": video["duration"],
        "file_size": video["file_size"],
        "thumbnail_url": video.get("thumbnail_path"),
        "uploaded_at": video["uploaded_at"]
    }
