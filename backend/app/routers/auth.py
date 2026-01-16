"""
认证相关 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.database import get_db
from app.models.user import UserCreate, UserLogin
from app.schemas.auth import RegisterResponse, LoginResponse, UserProfileResponse
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
    auth_service = AuthService(db)
    result = await auth_service.register(user_data)
    return result


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
    current_user: dict = Depends(get_current_user)
):
    """
    获取当前登录用户的个人信息
    
    需要认证：在 Header 中携带 `Authorization: Bearer {token}`
    """
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user.get("email"),
        "nickname": current_user.get("nickname"),
        "avatar_url": current_user.get("avatar_url"),
        "created_at": current_user["created_at"]
    }
