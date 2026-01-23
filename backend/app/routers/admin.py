"""
管理员 API 路由
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, status
from supabase import Client
from app.database import get_db
from app.models.points import PointsAdjustRequest, PurchaseRecord
from app.services.points_service import PointsService


router = APIRouter(prefix="/admin", tags=["管理员"])


# TODO: 添加管理员认证中间件
# def get_admin_user(...):
#     """获取当前管理员用户"""
#     pass


@router.get("/users", summary="获取用户列表")
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="搜索用户名或昵称"),
    db: Client = Depends(get_db)
):
    """
    获取用户列表（管理员）
    
    - **page**: 页码
    - **page_size**: 每页数量
    - **search**: 搜索关键词（用户名或昵称）
    """
    try:
        offset = (page - 1) * page_size
        
        # 先查询总数（使用单独的查询）
        count_query = db.table("users").select("id", count="exact")
        if search:
            count_query = count_query.or_(f"username.ilike.%{search}%,nickname.ilike.%{search}%")
        count_response = count_query.execute()
        total = count_response.count if hasattr(count_response, 'count') else len(count_response.data or [])
        
        # 再查询数据
        # 先尝试查询包含积分字段，如果失败则只查询基础字段
        data_query = None
        has_points_fields = False
        
        try:
            # 尝试查询包含积分字段
            data_query = db.table("users").select(
                "id, username, nickname, email, points, total_points_earned, total_points_spent, created_at"
            )
            # 先执行一次测试查询，看字段是否存在
            test_response = data_query.limit(1).execute()
            has_points_fields = True
        except Exception as e:
            # 如果积分字段不存在，只查询基础字段
            print(f"积分字段不存在，使用基础字段查询: {str(e)}")
            data_query = db.table("users").select(
                "id, username, nickname, email, created_at"
            )
            has_points_fields = False
        
        # 搜索条件
        if search:
            data_query = data_query.or_(f"username.ilike.%{search}%,nickname.ilike.%{search}%")
        
        # 查询数据
        response = data_query.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()
        
        # 处理返回数据，确保积分字段有默认值
        items = []
        for item in (response.data or []):
            processed_item = {
                "id": item.get("id"),
                "username": item.get("username"),
                "nickname": item.get("nickname"),
                "email": item.get("email"),
                "created_at": item.get("created_at")
            }
            # 如果有积分字段，添加；否则使用默认值0
            if has_points_fields:
                processed_item["points"] = item.get("points", 0)
                processed_item["total_points_earned"] = item.get("total_points_earned", 0)
                processed_item["total_points_spent"] = item.get("total_points_spent", 0)
            else:
                processed_item["points"] = 0
                processed_item["total_points_earned"] = 0
                processed_item["total_points_spent"] = 0
            
            items.append(processed_item)
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}"
        )


@router.get("/users/{user_id}", summary="获取用户详情")
async def get_user_detail(
    user_id: str,
    db: Client = Depends(get_db)
):
    """
    获取用户详细信息（管理员）
    """
    try:
        # 用户基本信息
        user_response = db.table("users").select("*").eq("id", user_id).execute()
        
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        user = user_response.data[0]
        
        # 用户统计信息
        videos_count = db.table("videos").select("id", count="exact").eq("user_id", user_id).execute()
        analyses_count = db.table("analyses").select("id", count="exact").eq("user_id", user_id).execute()
        purchases_count = db.table("purchase_records").select("id", count="exact").eq("user_id", user_id).execute()
        
        return {
            "user": user,
            "statistics": {
                "videos_count": videos_count.count if hasattr(videos_count, 'count') else len(videos_count.data or []),
                "analyses_count": analyses_count.count if hasattr(analyses_count, 'count') else len(analyses_count.data or []),
                "purchases_count": purchases_count.count if hasattr(purchases_count, 'count') else len(purchases_count.data or [])
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户详情失败: {str(e)}"
        )


@router.post("/points/adjust", summary="调整用户积分")
async def adjust_user_points(
    request: PointsAdjustRequest,
    db: Client = Depends(get_db)
):
    """
    调整用户积分（管理员）
    
    - **user_id**: 用户ID
    - **points**: 积分数量（正数增加，负数减少）
    - **description**: 调整原因
    - **transaction_type**: 交易类型（默认 'gift'）
    """
    points_service = PointsService(db)
    result = await points_service.adjust_points(
        user_id=request.user_id,
        points=request.points,
        transaction_type=request.transaction_type,
        description=request.description
    )
    return result


@router.get("/points/transactions", summary="获取积分交易记录")
async def get_points_transactions(
    user_id: Optional[str] = Query(None, description="用户ID（可选，不填则查询所有）"),
    transaction_type: Optional[str] = Query(None, description="交易类型"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Client = Depends(get_db)
):
    """
    获取积分交易记录（管理员）
    """
    try:
        offset = (page - 1) * page_size
        
        query = db.table("points_transactions").select("*")
        
        if user_id:
            query = query.eq("user_id", user_id)
        if transaction_type:
            query = query.eq("transaction_type", transaction_type)
        
        # 查询总数
        count_response = query.select("id", count="exact").execute()
        total = count_response.count if hasattr(count_response, 'count') else len(count_response.data or [])
        
        # 查询数据
        response = query.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": response.data or []
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取交易记录失败: {str(e)}"
        )


@router.get("/purchases", summary="获取购买记录列表")
async def get_purchases(
    user_id: Optional[str] = Query(None, description="用户ID（可选）"),
    payment_status: Optional[str] = Query(None, description="支付状态"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Client = Depends(get_db)
):
    """
    获取购买记录列表（管理员）
    """
    try:
        offset = (page - 1) * page_size
        
        query = db.table("purchase_records").select("*")
        
        if user_id:
            query = query.eq("user_id", user_id)
        if payment_status:
            query = query.eq("payment_status", payment_status)
        
        # 查询总数
        count_response = query.select("id", count="exact").execute()
        total = count_response.count if hasattr(count_response, 'count') else len(count_response.data or [])
        
        # 查询数据
        response = query.order("created_at", desc=True).range(offset, offset + page_size - 1).execute()
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": response.data or []
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取购买记录失败: {str(e)}"
        )


@router.get("/purchases/{purchase_id}", summary="获取购买记录详情")
async def get_purchase_detail(
    purchase_id: str,
    db: Client = Depends(get_db)
):
    """
    获取购买记录详情（管理员）
    """
    try:
        response = db.table("purchase_records").select("*").eq("id", purchase_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="购买记录不存在"
            )
        
        return response.data[0]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取购买记录详情失败: {str(e)}"
        )


@router.get("/analyses", summary="获取分析记录列表")
async def get_analyses(
    user_id: Optional[str] = Query(None, description="用户ID（可选，不填则查询所有）"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("analyzed_at", description="排序字段"),
    order: str = Query("desc", regex="^(asc|desc)$", description="排序方向"),
    db: Client = Depends(get_db)
):
    """
    获取分析记录列表（管理员）
    
    - **user_id**: 用户ID（可选）
    - **page**: 页码
    - **page_size**: 每页数量
    - **sort_by**: 排序字段（analyzed_at, speed, score）
    - **order**: 排序方向（asc 升序, desc 降序）
    """
    try:
        offset = (page - 1) * page_size
        
        # 先查询总数
        count_query = db.table("analyses").select("id", count="exact")
        if user_id:
            count_query = count_query.eq("user_id", user_id)
        count_response = count_query.execute()
        total = count_response.count if hasattr(count_response, 'count') else len(count_response.data or [])
        
        # 构建数据查询（尝试包含 points_cost 字段，如果不存在则只查询基础字段）
        try:
            # 先尝试查询包含 points_cost 字段
            data_query = db.table("analyses").select(
                "id, user_id, video_id, speed, level, score, technique_power, technique_angle, technique_coordination, rank, rank_position, points_cost, analyzed_at, analysis_duration, videos(original_filename, thumbnail_path), users(username, nickname)"
            )
            # 测试查询，看字段是否存在
            test_response = data_query.limit(1).execute()
            has_points_cost = True
        except Exception as e:
            # 如果 points_cost 字段不存在，只查询基础字段
            print(f"points_cost 字段不存在，使用基础字段查询: {str(e)}")
            data_query = db.table("analyses").select(
                "id, user_id, video_id, speed, level, score, technique_power, technique_angle, technique_coordination, rank, rank_position, analyzed_at, analysis_duration, videos(original_filename, thumbnail_path), users(username, nickname)"
            )
            has_points_cost = False
        
        if user_id:
            data_query = data_query.eq("user_id", user_id)
        
        # 排序
        ascending = (order == "asc")
        data_query = data_query.order(sort_by, desc=not ascending)
        
        # 查询数据
        response = data_query.range(offset, offset + page_size - 1).execute()
        
        # 格式化结果
        items = []
        for record in (response.data or []):
            video_info = record.get("videos", {}) if isinstance(record.get("videos"), dict) else {}
            user_info = record.get("users", {}) if isinstance(record.get("users"), dict) else {}
            
            # 处理缩略图 URL
            thumbnail_path = video_info.get("thumbnail_path") if video_info else None
            thumbnail_url = None
            if thumbnail_path:
                if thumbnail_path.startswith("/uploads/"):
                    thumbnail_url = thumbnail_path
                elif "thumbnails" in thumbnail_path:
                    parts = thumbnail_path.split("thumbnails")
                    if len(parts) > 1:
                        thumbnail_url = f"/uploads/thumbnails{parts[1]}"
                    else:
                        thumbnail_url = thumbnail_path
                else:
                    thumbnail_url = f"/uploads/{thumbnail_path}"
            
            items.append({
                "id": record["id"],
                "user_id": record["user_id"],
                "user_info": {
                    "username": user_info.get("username") if user_info else None,
                    "nickname": user_info.get("nickname") if user_info else None
                },
                "video_id": record["video_id"],
                "video_info": {
                    "original_filename": video_info.get("original_filename") if video_info else None,
                    "thumbnail_url": thumbnail_url
                },
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
                "points_cost": record.get("points_cost", 0) if has_points_cost else 0,  # 如果字段不存在，使用默认值0
                "analyzed_at": record["analyzed_at"],
                "analysis_duration": record.get("analysis_duration")
            })
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分析记录失败: {str(e)}"
        )


@router.get("/analyses/{analysis_id}", summary="获取分析记录详情")
async def get_analysis_detail(
    analysis_id: str,
    db: Client = Depends(get_db)
):
    """
    获取分析记录详情（管理员）
    """
    try:
        # 查询分析记录和关联信息
        response = db.table("analyses").select(
            "*, videos(*), users(username, nickname, email)"
        ).eq("id", analysis_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="分析记录不存在"
            )
        
        record = response.data[0]
        video = record.pop("videos", {}) if isinstance(record.get("videos"), dict) else {}
        user = record.pop("users", {}) if isinstance(record.get("users"), dict) else {}
        
        # 处理缩略图 URL
        thumbnail_path = video.get("thumbnail_path") if video else None
        thumbnail_url = None
        if thumbnail_path:
            if thumbnail_path.startswith("/uploads/"):
                thumbnail_url = thumbnail_path
            elif "thumbnails" in thumbnail_path:
                parts = thumbnail_path.split("thumbnails")
                if len(parts) > 1:
                    thumbnail_url = f"/uploads/thumbnails{parts[1]}"
                else:
                    thumbnail_url = thumbnail_path
            else:
                thumbnail_url = f"/uploads/{thumbnail_path}"
        
        return {
            "analysis": {
                "id": record["id"],
                "user_id": record["user_id"],
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
                "suggestions": record.get("suggestions"),
                "points_cost": record.get("points_cost", 0),
                "analyzed_at": record["analyzed_at"],
                "analysis_duration": record.get("analysis_duration")
            },
            "video": {
                "id": video.get("id"),
                "original_filename": video.get("original_filename"),
                "duration": video.get("duration"),
                "file_size": video.get("file_size"),
                "thumbnail_url": thumbnail_url,
                "uploaded_at": video.get("uploaded_at")
            } if video else None,
            "user": {
                "id": record["user_id"],
                "username": user.get("username") if user else None,
                "nickname": user.get("nickname") if user else None,
                "email": user.get("email") if user else None
            } if user else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取分析记录详情失败: {str(e)}"
        )


@router.get("/users/{user_id}/analyses", summary="获取用户的分析记录")
async def get_user_analyses(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("analyzed_at", description="排序字段"),
    order: str = Query("desc", regex="^(asc|desc)$", description="排序方向"),
    db: Client = Depends(get_db)
):
    """
    获取指定用户的分析记录（管理员）
    """
    try:
        # 检查用户是否存在
        user_check = db.table("users").select("id").eq("id", user_id).execute()
        if not user_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        offset = (page - 1) * page_size
        
        # 构建查询
        query = db.table("analyses").select(
            "id, video_id, speed, level, score, technique_power, technique_angle, technique_coordination, rank, rank_position, points_cost, analyzed_at, analysis_duration, videos(original_filename, thumbnail_path)"
        ).eq("user_id", user_id)
        
        # 排序
        ascending = (order == "asc")
        query = query.order(sort_by, desc=not ascending)
        
        # 查询总数
        count_response = db.table("analyses").select("id", count="exact").eq("user_id", user_id).execute()
        total = count_response.count if hasattr(count_response, 'count') else len(count_response.data or [])
        
        # 查询数据
        response = query.range(offset, offset + page_size - 1).execute()
        
        # 格式化结果
        items = []
        for record in (response.data or []):
            video_info = record.get("videos", {}) if isinstance(record.get("videos"), dict) else {}
            
            # 处理缩略图 URL
            thumbnail_path = video_info.get("thumbnail_path") if video_info else None
            thumbnail_url = None
            if thumbnail_path:
                if thumbnail_path.startswith("/uploads/"):
                    thumbnail_url = thumbnail_path
                elif "thumbnails" in thumbnail_path:
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
                "video_info": {
                    "original_filename": video_info.get("original_filename") if video_info else None,
                    "thumbnail_url": thumbnail_url
                },
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
                "points_cost": record.get("points_cost", 0),
                "analyzed_at": record["analyzed_at"],
                "analysis_duration": record.get("analysis_duration")
            })
        
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": items
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户分析记录失败: {str(e)}"
        )


@router.get("/statistics", summary="获取统计数据")
async def get_statistics(
    db: Client = Depends(get_db)
):
    """
    获取系统统计数据（管理员）
    """
    try:
        # 用户统计
        users_count = db.table("users").select("id", count="exact").execute()
        
        # 尝试查询积分（如果字段存在）
        total_points_sum = 0
        try:
            total_points = db.table("users").select("points").execute()
            total_points_sum = sum(user.get("points", 0) for user in (total_points.data or []))
        except Exception:
            # 积分字段不存在，使用默认值0
            print("积分字段不存在，使用默认值0")
        
        # 分析统计
        analyses_count = db.table("analyses").select("id", count="exact").execute()
        
        # 购买统计（如果表存在）
        purchases_count = 0
        total_revenue = 0.0
        try:
            purchases_count_query = db.table("purchase_records").select("id", count="exact").execute()
            purchases_count = purchases_count_query.count if hasattr(purchases_count_query, 'count') else len(purchases_count_query.data or [])
            
            paid_purchases = db.table("purchase_records").select("price").eq("payment_status", "paid").execute()
            total_revenue = sum(float(record.get("price", 0)) for record in (paid_purchases.data or []))
        except Exception:
            # 购买记录表不存在，使用默认值
            print("购买记录表不存在，使用默认值")
        
        return {
            "users": {
                "total": users_count.count if hasattr(users_count, 'count') else len(users_count.data or []),
                "total_points": total_points_sum
            },
            "analyses": {
                "total": analyses_count.count if hasattr(analyses_count, 'count') else len(analyses_count.data or [])
            },
            "purchases": {
                "total": purchases_count,
                "total_revenue": total_revenue
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计数据失败: {str(e)}"
        )
