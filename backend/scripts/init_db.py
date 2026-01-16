"""
数据库初始化脚本
在 Supabase 中创建所需的表
"""
import sys
import os

# 添加父目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Database


# SQL 语句
CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
"""

CREATE_VIDEOS_TABLE = """
CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    duration FLOAT NOT NULL,
    thumbnail_path TEXT,
    trim_start FLOAT DEFAULT 0,
    trim_end FLOAT,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_videos_user_id ON videos(user_id);
CREATE INDEX IF NOT EXISTS idx_videos_uploaded_at ON videos(uploaded_at DESC);
"""

CREATE_ANALYSES_TABLE = """
CREATE TABLE IF NOT EXISTS analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    video_id UUID NOT NULL REFERENCES videos(id) ON DELETE CASCADE,
    speed INTEGER NOT NULL,
    level VARCHAR(50) NOT NULL,
    score FLOAT NOT NULL,
    technique_power INTEGER NOT NULL,
    technique_angle INTEGER NOT NULL,
    technique_coordination INTEGER NOT NULL,
    rank INTEGER,
    rank_position INTEGER,
    suggestions JSONB,
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    analysis_duration FLOAT
);

CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_video_id ON analyses(video_id);
CREATE INDEX IF NOT EXISTS idx_analyses_analyzed_at ON analyses(analyzed_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_speed ON analyses(speed DESC);
"""


def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    try:
        db = Database.get_client()
        
        # 注意：Supabase 的 Python 客户端不直接支持执行 SQL
        # 需要在 Supabase Dashboard 的 SQL Editor 中手动执行这些语句
        
        print("\n" + "=" * 70)
        print("⚠️  请在 Supabase Dashboard 的 SQL Editor 中执行以下 SQL 语句：")
        print("=" * 70)
        print("\n-- 1. 创建 users 表")
        print(CREATE_USERS_TABLE)
        print("\n-- 2. 创建 videos 表")
        print(CREATE_VIDEOS_TABLE)
        print("\n-- 3. 创建 analyses 表")
        print(CREATE_ANALYSES_TABLE)
        print("\n" + "=" * 70)
        print("\n💡 提示：")
        print("1. 访问: https://app.supabase.com")
        print("2. 选择你的项目")
        print("3. 点击左侧菜单 'SQL Editor'")
        print("4. 新建查询，粘贴上述 SQL 并执行")
        print("=" * 70)
        
        # 测试连接
        response = db.table("users").select("id").limit(1).execute()
        print("\n✅ 数据库连接测试成功！")
        print("如果表已存在，你可以开始使用 API 了。")
        
    except Exception as e:
        print(f"\n❌ 数据库连接失败: {str(e)}")
        print("\n请检查 .env 文件中的 Supabase 配置：")
        print("- SUPABASE_URL")
        print("- SUPABASE_KEY")
        sys.exit(1)


if __name__ == "__main__":
    init_database()
