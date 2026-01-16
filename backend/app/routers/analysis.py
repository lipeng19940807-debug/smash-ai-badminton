"""
分析相关 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.database import get_db
from app.models.analysis import AnalysisStartRequest, AnalysisResult
from app.services.analysis_service import AnalysisService
from app.dependencies import get_current_user


router = APIRouter(prefix="/analysis", tags=["AI分析"])


@router.post("/start", response_model=AnalysisResult, summary="开始分析视频")
async def start_analysis(
    request: AnalysisStartRequest,
    current_user: dict = Depends(get_current_user),
    db: Client = Depends(get_db)
):
    """
    开始分析视频
    
    - **video_id**: 要分析的视频ID
    
    调用 Gemini API 分析视频，返回杀球速度、技术评分和改进建议
    
    分析过程可能需要 10-30 秒，请耐心等待
    """
    analysis_service = AnalysisService(db)
    result = await analysis_service.analyze_video(request.video_id, current_user["id"])
    return result


@router.get("/{analysis_id}", response_model=AnalysisResult, summary="获取分析结果")
async def get_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    db: Client = Depends(get_db)
):
    """
    获取分析结果
    
    - **analysis_id**: 分析记录ID
    
    返回之前保存的分析结果
    """
    analysis_service = AnalysisService(db)
    result = await analysis_service.get_analysis(analysis_id, current_user["id"])
    return result
