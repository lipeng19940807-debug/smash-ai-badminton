"""
认证服务
处理用户注册、登录等业务逻辑
"""
from datetime import timedelta
from typing import Optional
from fastapi import HTTPException, status
from supabase import Client
from app.models.user import UserCreate, UserLogin
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.config import settings


class AuthService:
    """认证服务类"""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def register(self, user_data: UserCreate) -> dict:
        """
        用户注册
        
        Args:
            user_data: 用户注册数据
        
        Returns:
            包含用户信息和 token 的字典
        
        Raises:
            HTTPException: 如果用户名已存在
        """
        # 检查用户名是否已存在
        existing_user = self.db.table("users").select("id").eq("username", user_data.username).execute()
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在（如果提供了邮箱）
        if user_data.email:
            existing_email = self.db.table("users").select("id").eq("email", user_data.email).execute()
            if existing_email.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被注册"
                )
        
        # 创建用户
        password_hash = get_password_hash(user_data.password)
        
        user_dict = {
            "username": user_data.username,
            "email": user_data.email,
            "nickname": user_data.nickname or user_data.username,
            "password_hash": password_hash,
        }
        
        try:
            response = self.db.table("users").insert(user_dict).execute()
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="创建用户失败"
                )
            
            created_user = response.data[0]
            
            # 生成 JWT Token
            access_token = create_access_token(
                data={"sub": created_user["id"]},
                expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
            )
            
            return {
                "id": created_user["id"],
                "username": created_user["username"],
                "nickname": created_user["nickname"],
                "token": access_token
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"注册失败: {str(e)}"
            )
    
    async def login(self, login_data: UserLogin) -> dict:
        """
        用户登录
        
        Args:
            login_data: 登录数据
        
        Returns:
            包含 token 和用户信息的字典
        
        Raises:
            HTTPException: 如果用户名或密码错误
        """
        # 查询用户
        try:
            response = self.db.table("users").select("*").eq("username", login_data.username).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户名或密码错误"
                )
            
            user = response.data[0]
            
            # 验证密码
            if not verify_password(login_data.password, user["password_hash"]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="用户名或密码错误"
                )
            
            # 生成 JWT Token
            access_token = create_access_token(
                data={"sub": user["id"]},
                expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
            )
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "nickname": user.get("nickname"),
                    "avatar_url": user.get("avatar_url"),
                }
            }
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"登录失败: {str(e)}"
            )
    
    async def get_user_profile(self, user_id: str) -> dict:
        """
        获取用户个人资料
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户信息字典
        """
        try:
            response = self.db.table("users").select("id, username, email, nickname, avatar_url, created_at").eq("id", user_id).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            
            return response.data[0]
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取用户信息失败: {str(e)}"
            )
