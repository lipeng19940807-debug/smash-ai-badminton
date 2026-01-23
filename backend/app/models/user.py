"""
Pydantic 数据模型 - 用户
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    wechat_openid: Optional[str] = None
    nickname: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: str
    password_hash: str
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class User(UserBase):
    """用户响应模型（不包含密码）"""
    id: str
    avatar_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
