"""
依赖注入函数
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from app.database import get_db
from app.utils.security import decode_access_token
from app.models.user import User


# HTTP Bearer Token 认证方案
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Client = Depends(get_db)
) -> dict:
    """
    获取当前登录用户
    
    支持两种认证方式：
    1. 微信云托管自动注入的 X-WX-OPENID (优先级高)
    2. 标准 JWT Token (Authorization Header)
    """
    # 1. 尝试从微信云托管请求头获取 OpenID
    openid = request.headers.get("X-WX-OPENID")
    if openid:
        # 如果有 OpenID，说明是云托管环境，直接根据 OpenID 查询或创建用户
        try:
            # 在云托管环境下，id 可能就是 openid 或者关联 openid
            response = db.table("users").select("*").eq("username", openid).execute()
            if response.data:
                return response.data[0]
            else:
                # 如果用户不存在，可以自动创建一个基础用户
                new_user = {
                    "username": openid,
                    "nickname": "微信用户",
                    "email": f"{openid[:10]}@wechat.com"
                }
                insert_res = db.table("users").insert(new_user).execute()
                if insert_res.data:
                    return insert_res.data[0]
        except Exception as e:
            print(f"云托管 OpenID 认证失败: {str(e)}")
            # 继续尝试 JWT 认证

    # 2. 尝试 JWT Token 认证
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token = credentials.credentials
    
    # 解码 Token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 获取用户 ID
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从数据库查询用户
    try:
        response = db.table("users").select("*").eq("id", user_id).execute()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在"
            )
        
        user_data = response.data[0]
        return user_data
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Client = Depends(get_db)
) -> Optional[dict]:
    """
    获取当前用户（可选）
    
    如果没有提供 Token 或 Token 无效，返回 None 而不是抛出异常
    用于可选认证的端点
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None
