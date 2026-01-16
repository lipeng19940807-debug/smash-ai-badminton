"""
Pydantic 数据模型 - 分析结果
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TechniqueScore(BaseModel):
    """技术评分"""
    power: int = Field(..., ge=0, le=100)
    angle: int = Field(..., ge=0, le=100)
    coordination: int = Field(..., ge=0, le=100)


class Suggestion(BaseModel):
    """改进建议"""
    title: str
    desc: str
    icon: str
    highlight: str


class AnalysisBase(BaseModel):
    """分析结果基础模型"""
    speed: int = Field(..., gt=0)
    level: str
    score: float = Field(..., ge=0, le=10)
    technique: TechniqueScore
    rank: Optional[int] = Field(None, ge=0, le=100)
    rank_position: Optional[int] = Field(None, ge=0, le=100)
    suggestions: List[Suggestion]


class AnalysisCreate(AnalysisBase):
    """分析结果创建模型"""
    user_id: str
    video_id: str
    analysis_duration: Optional[float] = None


class AnalysisInDB(AnalysisCreate):
    """数据库中的分析模型"""
    id: str
    analyzed_at: datetime


class AnalysisResult(AnalysisBase):
    """分析结果响应模型"""
    id: str
    video_id: str
    analyzed_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisStartRequest(BaseModel):
    """开始分析请求"""
    video_id: str


class AnalysisWithVideo(BaseModel):
    """分析结果 + 视频信息"""
    analysis: AnalysisResult
    video: dict  # 包含视频的基本信息
