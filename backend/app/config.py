"""
应用配置管理
使用 Pydantic Settings 管理环境变量
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """应用配置"""
    
    # Supabase 配置
    supabase_url: str
    supabase_key: str
    
    # JWT 配置
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7天
    
    # Gemini API 配置
    gemini_api_key: str
    
    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000  # 默认值，会被环境变量 PORT 覆盖
    
    # 文件存储配置
    upload_dir: str = "./uploads"
    max_video_size_mb: int = 50
    max_video_duration_seconds: int = 10
    allowed_extensions: str = "mp4,mov,avi,mkv,webm"
    
    # CORS 配置
    allowed_origins: str = "http://localhost:4200"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """获取允许的文件扩展名列表"""
        return [ext.strip().lower() for ext in self.allowed_extensions.split(",")]
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """获取允许的跨域来源列表"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def max_video_size_bytes(self) -> int:
        """获取最大视频文件大小（字节）"""
        return self.max_video_size_mb * 1024 * 1024


# 创建全局配置实例
settings = Settings()
