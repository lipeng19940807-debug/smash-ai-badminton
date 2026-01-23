"""
Pydantic 数据模型 - 视频
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class VideoBase(BaseModel):
    """视频基础模型"""
    original_filename: str
    duration: float = Field(..., gt=0)
    file_size: int = Field(..., gt=0)


class VideoCreate(VideoBase):
    """视频创建模型"""
    user_id: str
    stored_filename: str
    file_path: str
    thumbnail_path: Optional[str] = None
    trim_start: float = 0.0
    trim_end: Optional[float] = None


class VideoInDB(VideoCreate):
    """数据库中的视频模型"""
    id: str
    uploaded_at: datetime


class Video(BaseModel):
    """视频响应模型"""
    id: str
    original_filename: str
    duration: float
    file_size: int
    thumbnail_url: Optional[str] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class VideoUploadResponse(BaseModel):
    """视频上传响应"""
    id: str
    original_filename: str
    file_path: str
    duration: float
    file_size: int
    thumbnail_path: Optional[str] = None
    uploaded_at: datetime


class CloudVideoUploadRequest(BaseModel):
    """微信云存储视频同步请求"""
    file_id: str
    trim_start: Optional[float] = None
    trim_end: Optional[float] = None
