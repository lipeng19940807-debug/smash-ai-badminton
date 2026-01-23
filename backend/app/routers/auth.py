"""
认证相关 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.database import get_db
from app.models.user import UserCreate, UserLogin
from app.schemas.auth import RegisterResponse, LoginResponse, UserProfileResponse, WeChatLoginRequest
from app.services.auth_service import AuthService
from app.dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=RegisterResponse, summary="用户注册")
async def register(
    user_data: UserCreate,
    db: Client = Depends(get_db)
):
    """
    用户注册
    
    - **username**: 用户名 (3-50字符)
    - **password**: 密码 (至少6字符)
    - **email**: 邮箱 (可选)
    - **nickname**: 昵称 (可选)
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.register(user_data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"注册路由异常: {str(e)}")
        print(f"错误堆栈: {error_trace}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(
    login_data: UserLogin,
    db: Client = Depends(get_db)
):
    """
    用户登录
    
    - **username**: 用户名
    - **password**: 密码
    
    返回 JWT Token，后续请求需在 Header 中携带: `Authorization: Bearer {token}`
    """
    auth_service = AuthService(db)
    result = await auth_service.login(login_data)
    return result


@router.get("/profile", response_model=UserProfileResponse, summary="获取用户信息")
async def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Client = Depends(get_db)
):
    """
    获取当前登录用户的个人信息（包含积分信息）
    
    需要认证：在 Header 中携带 `Authorization: Bearer {token}`
    """
    # 从数据库获取最新的用户信息（包含积分）
    try:
        user_response = db.table("users").select(
            "id, username, email, nickname, avatar_url, points, total_points_earned, total_points_spent, created_at"
        ).eq("id", current_user["id"]).execute()
        
        if user_response.data:
            user_data = user_response.data[0]
            return {
                "id": user_data["id"],
                "username": user_data["username"],
                "email": user_data.get("email"),
                "nickname": user_data.get("nickname"),
                "avatar_url": user_data.get("avatar_url"),
                "points": user_data.get("points", 0),
                "total_points_earned": user_data.get("total_points_earned", 0),
                "total_points_spent": user_data.get("total_points_spent", 0),
                "created_at": str(user_data["created_at"])
            }
    except Exception as e:
        # 如果查询失败，返回基础信息
        pass
    
    # 降级返回：使用 current_user 中的信息
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user.get("email"),
        "nickname": current_user.get("nickname"),
        "avatar_url": current_user.get("avatar_url"),
        "points": current_user.get("points", 0),
        "total_points_earned": current_user.get("total_points_earned", 0),
        "total_points_spent": current_user.get("total_points_spent", 0),
        "created_at": str(current_user.get("created_at", ""))
    }


@router.post("/wechat", response_model=LoginResponse, summary="微信小程序登录")
async def wechat_login(
    login_data: WeChatLoginRequest,
    db: Client = Depends(get_db)
):
    """
    微信一键登录
    
    接收小程序的 code，返回 JWT Token
    自动注册新用户
    """
    auth_service = AuthService(db)
    result = await auth_service.wechat_login(login_data)
    return result
