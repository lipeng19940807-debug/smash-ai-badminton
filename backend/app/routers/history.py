"""
历史记录相关 API 路由
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from supabase import Client
from pydantic import BaseModel
from app.database import get_db
from app.dependencies import get_current_user


router = APIRouter(prefix="/history", tags=["历史记录"])


class HistoryItem(BaseModel):
    """历史记录列表项"""
    id: str
    video_id: str
    speed: int
    score: float
    level: str
    thumbnail_url: Optional[str]
    analyzed_at: str


class HistoryResponse(BaseModel):
    """历史记录响应"""
    total: int
    page: int
    page_size: int
    items: List[HistoryItem]


@router.get("", response_model=HistoryResponse, summary="获取历史记录列表")
async def get_history(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    sort_by: str = Query("analyzed_at", description="排序字段"),
    order: str = Query("desc", regex="^(asc|desc)$", description="排序方向"),
    current_user: dict = Depends(get_current_user),
    db: Client = Depends(get_db)
):
    """
    获取用户的历史分析记录
    
    - **page**: 页码（从1开始）
    - **page_size**: 每页记录数（1-50）
    - **sort_by**: 排序字段（analyzed_at, speed, score）
    - **order**: 排序方向（asc 升序, desc 降序）
    
    返回分页的历史记录列表
    """
    user_id = current_user["id"]
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 查询总数
    count_response = db.table("analyses").select("id", count="exact").eq("user_id", user_id).execute()
    total = count_response.count if hasattr(count_response, 'count') else len(count_response.data or [])
    
    # 查询分析记录（联表查询视频信息获取缩略图）
    query = db.table("analyses").select(
        "id, video_id, speed, score, level, analyzed_at, videos(thumbnail_path)"
    ).eq("user_id", user_id)
    
    # 排序
    ascending = (order == "asc")
    query = query.order(sort_by, desc=not ascending)
    
    # 分页
    query = query.range(offset, offset + page_size - 1)
    
    response = query.execute()
    
    # 格式化结果
    items = []
    for record in response.data:
        video_info = record.get("videos", {}) if isinstance(record.get("videos"), dict) else {}
        thumbnail_path = video_info.get("thumbnail_path") if video_info else None
        
        # 转换缩略图路径为 URL
        thumbnail_url = None
        if thumbnail_path:
            # 将本地路径转换为可访问的 URL
            if thumbnail_path.startswith("./"):
                thumbnail_path = thumbnail_path[2:]
            elif not thumbnail_path.startswith("/"):
                thumbnail_path = "/" + thumbnail_path
            # 确保路径以 /uploads 开头
            if thumbnail_path.startswith("/uploads/"):
                thumbnail_url = thumbnail_path
            else:
                # 从完整路径中提取相对路径
                if "thumbnails" in thumbnail_path:
                    parts = thumbnail_path.split("thumbnails")
                    if len(parts) > 1:
                        thumbnail_url = f"/uploads/thumbnails{parts[1]}"
                    else:
                        thumbnail_url = thumbnail_path
                else:
                    thumbnail_url = f"/uploads/{thumbnail_path}"
        
        items.append({
            "id": record["id"],
            "video_id": record["video_id"],
            "speed": record["speed"],
            "score": record["score"],
            "level": record["level"],
            "thumbnail_url": thumbnail_url,
            "analyzed_at": record["analyzed_at"]
        })
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    }


@router.get("/{analysis_id}/detail", summary="获取历史记录详情")
async def get_history_detail(
    analysis_id: str,
    current_user: dict = Depends(get_current_user),
    db: Client = Depends(get_db)
):
    """
    获取单条历史记录的详细信息
    
    - **analysis_id**: 分析记录ID
    
    返回完整的分析结果和视频信息
    """
    user_id = current_user["id"]
    
    # 查询分析记录和视频信息
    analysis_response = db.table("analyses").select(
        "*, videos(*)"
    ).eq("id", analysis_id).eq("user_id", user_id).execute()
    
    if not analysis_response.data:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    record = analysis_response.data[0]
    video = record.pop("videos", {})
    
    return {
        "analysis": {
            "id": record["id"],
            "video_id": record["video_id"],
            "speed": record["speed"],
            "level": record["level"],
            "score": record["score"],
            "technique": {
                "power": record["technique_power"],
                "angle": record["technique_angle"],
                "coordination": record["technique_coordination"]
            },
            "rank": record.get("rank"),
            "rank_position": record.get("rank_position"),
            "suggestions": record["suggestions"],
            "analyzed_at": record["analyzed_at"]
        },
        "video": {
            "id": video.get("id"),
            "original_filename": video.get("original_filename"),
            "duration": video.get("duration"),
            "file_size": video.get("file_size"),
            "thumbnail_url": video.get("thumbnail_path"),
            "uploaded_at": video.get("uploaded_at")
        } if video else None
    }
