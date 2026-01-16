"""
Supabase 数据库连接管理
"""
from supabase import create_client, Client
from app.config import settings


class Database:
    """数据库连接管理类"""
    
    _client: Client = None
    
    @classmethod
    def get_client(cls) -> Client:
        """获取 Supabase 客户端实例（单例模式）"""
        if cls._client is None:
            cls._client = create_client(
                supabase_url=settings.supabase_url,
                supabase_key=settings.supabase_key
            )
        return cls._client
    
    @classmethod
    def close(cls):
        """关闭数据库连接"""
        if cls._client is not None:
            # Supabase client 不需要显式关闭
            cls._client = None


# 依赖注入函数
def get_db() -> Client:
    """FastAPI 依赖注入：获取数据库客户端"""
    return Database.get_client()
