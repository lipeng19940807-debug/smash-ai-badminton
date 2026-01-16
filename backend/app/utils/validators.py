"""
数据验证工具函数
"""
import os
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from app.config import settings


def validate_video_file(file: UploadFile) -> None:
    """
    验证上传的视频文件
    
    Args:
        file: 上传的文件对象
    
    Raises:
        HTTPException: 如果文件不符合要求
    """
    # 检查文件扩展名
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不能为空"
        )
    
    file_ext = file.filename.rsplit('.', 1)[-1].lower()
    if file_ext not in settings.allowed_extensions_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式。允许的格式: {', '.join(settings.allowed_extensions_list)}"
        )
    
    # 检查 Content-Type
    if file.content_type and not file.content_type.startswith('video/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件必须是视频格式"
        )


def validate_video_size(file_size: int) -> None:
    """
    验证视频文件大小
    
    Args:
        file_size: 文件大小（字节）
    
    Raises:
        HTTPException: 如果文件过大
    """
    if file_size > settings.max_video_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"视频文件过大。最大允许 {settings.max_video_size_mb}MB"
        )


def validate_trim_range(trim_start: Optional[float], trim_end: Optional[float], duration: float) -> tuple:
    """
    验证视频裁剪范围
    
    Args:
        trim_start: 裁剪起始时间（秒）
        trim_end: 裁剪结束时间（秒）
        duration: 视频总时长（秒）
    
    Returns:
        (validated_start, validated_end) 元组
    
    Raises:
        HTTPException: 如果裁剪范围无效
    """
    start = trim_start if trim_start is not None else 0.0
    end = trim_end if trim_end is not None else duration
    
    # 验证范围有效性
    if start < 0 or start >= duration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"裁剪起始时间无效。必须在 0 到 {duration:.2f} 秒之间"
        )
    
    if end <= start or end > duration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"裁剪结束时间无效。必须大于起始时间且不超过 {duration:.2f} 秒"
        )
    
    # 检查裁剪后的时长
    trimmed_duration = end - start
    if trimmed_duration > settings.max_video_duration_seconds:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"裁剪后的视频时长不能超过 {settings.max_video_duration_seconds} 秒"
        )
    
    return (start, end)
