"""数据模型模块"""
from app.models.user import User, UserCreate, UserLogin, UserInDB
from app.models.video import Video, VideoCreate, VideoInDB, VideoUploadResponse
from app.models.analysis import (
    AnalysisResult,
    AnalysisCreate,
    AnalysisInDB,
    AnalysisStartRequest,
    TechniqueScore,
    Suggestion,
    AnalysisWithVideo
)

__all__ = [
    "User",
    "UserCreate",
    "UserLogin",
    "UserInDB",
    "Video",
    "VideoCreate",
    "VideoInDB",
    "VideoUploadResponse",
    "AnalysisResult",
    "AnalysisCreate",
    "AnalysisInDB",
    "AnalysisStartRequest",
    "TechniqueScore",
    "Suggestion",
    "AnalysisWithVideo",
]
