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
        
        # 基础用户数据（不包含积分字段，避免字段不存在导致错误）
        user_dict = {
            "username": user_data.username,
            "email": user_data.email,
            "nickname": user_data.nickname or user_data.username,
            "password_hash": password_hash
        }
        
        # 注意：不在这里添加积分字段
        # 如果数据库表有积分字段，可以通过触发器或后续更新来设置
        # 这样可以避免字段不存在时的错误
        
        try:
            print(f"准备创建用户: username={user_data.username}, email={user_data.email}")
            response = self.db.table("users").insert(user_dict).execute()
            
            if not response.data:
                print("创建用户失败: 响应为空")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="创建用户失败：服务器响应为空"
                )
            
            created_user = response.data[0]
            print(f"用户创建成功: ID={created_user.get('id')}, username={created_user.get('username')}")
            
            # 尝试赠送积分（如果积分系统已配置）
            # 先检查返回的用户数据中是否有积分字段
            has_points_field = "points" in created_user
            
            if has_points_field:
                # 如果数据库有积分字段，尝试赠送积分
                if created_user.get("points", 0) == 0:
                    try:
                        from app.services.points_service import PointsService
                        points_service = PointsService(self.db)
                        await points_service.adjust_points(
                            user_id=created_user["id"],
                            points=50,
                            transaction_type="gift",
                            description="新用户注册奖励",
                            related_type="welcome_bonus"
                        )
                        print(f"成功赠送新用户积分: user_id={created_user['id']}")
                        # 重新获取用户信息
                        updated_response = self.db.table("users").select("*").eq("id", created_user["id"]).execute()
                        if updated_response.data:
                            created_user = updated_response.data[0]
                    except Exception as e:
                        import traceback
                        error_trace = traceback.format_exc()
                        print(f"自动赠送积分失败（可能积分系统未配置）: {str(e)}")
                        print(f"错误堆栈: {error_trace}")
                        # 积分赠送失败不影响注册流程
            else:
                print("数据库表没有积分字段，跳过积分赠送（这是正常的，如果还未初始化积分系统）")
            
            # 生成 JWT Token
            access_token = create_access_token(
                data={"sub": created_user["id"]},
                expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
            )
            
            # 返回注册响应（与 RegisterResponse schema 一致）
            return {
                "id": created_user["id"],
                "username": created_user["username"],
                "nickname": created_user.get("nickname") or created_user["username"],
                "token": access_token  # 注意：前端期望的是 token 字段
            }
        
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            error_msg = str(e)
            print(f"注册失败: {error_msg}")
            print(f"错误堆栈: {error_trace}")
            print(f"尝试插入的数据: {user_dict}")
            
            # 提供更详细的错误信息
            if "column" in error_msg.lower() and "does not exist" in error_msg.lower():
                detail_msg = "数据库表结构不匹配，请检查数据库是否已初始化积分字段"
            elif "duplicate key" in error_msg.lower() or "unique constraint" in error_msg.lower():
                detail_msg = "用户名或邮箱已被注册"
            elif "null value" in error_msg.lower() or "not null" in error_msg.lower():
                detail_msg = "必填字段缺失，请检查输入数据"
            else:
                detail_msg = f"注册失败: {error_msg}"
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=detail_msg
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
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取用户信息失败: {str(e)}"
            )

    async def wechat_login(self, login_data) -> dict:
        """
        微信一键登录
        """
        from app.utils.wechat import get_wechat_openid
        import secrets
        
        # 1. 获取 openid
        openid = await get_wechat_openid(login_data.code)
        
        # 2. 查找用户
        response = self.db.table("users").select("*").eq("wechat_openid", openid).execute()
        
        user = None
        if response.data:
            user = response.data[0]
            # 更新用户信息（如果提供了）
            if login_data.nickname or login_data.avatar_url:
                update_data = {}
                if login_data.nickname:
                    update_data["nickname"] = login_data.nickname
                if login_data.avatar_url:
                    update_data["avatar_url"] = login_data.avatar_url
                self.db.table("users").update(update_data).eq("id", user["id"]).execute()
        else:
            # 3. 注册新用户
            # 生成随机密码 (用户不会用到这个密码，除非他们后来绑定了邮箱/手机)
            random_password = secrets.token_urlsafe(16)
            password_hash = get_password_hash(random_password)
            
            # 生成唯一用户名
            username = f"wx_{openid[-8:]}_{secrets.token_hex(2)}"
            
            new_user = {
                "username": username,
                "wechat_openid": openid,
                "password_hash": password_hash,
                "nickname": login_data.nickname or f"用户{username[-4:]}",
                "avatar_url": login_data.avatar_url
            }
            
            try:
                insert_res = self.db.table("users").insert(new_user).execute()
                if insert_res.data:
                    user = insert_res.data[0]
                else:
                    raise Exception("Create user returned no data")
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"创建微信用户失败: {str(e)}"
                )
        
        # 4. 生成 Token
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
