"""
API 请求/响应 Schema - 认证
"""
from typing import Optional
from pydantic import BaseModel


class TokenResponse(BaseModel):
    """Token 响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class RegisterResponse(BaseModel):
    """注册响应模型"""
    id: str
    username: str
    nickname: Optional[str] = None
    token: str


class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserProfileResponse(BaseModel):
    """用户信息响应模型"""
    id: str
    username: str
    email: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    points: int = 0
    total_points_earned: int = 0
    total_points_spent: int = 0
    created_at: str


class WeChatLoginRequest(BaseModel):
    """微信登录请求模型"""
    code: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
