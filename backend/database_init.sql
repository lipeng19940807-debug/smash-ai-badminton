-- 羽毛球杀球分析系统 - 数据库初始化脚本
-- 在 Supabase SQL Editor 中执行此脚本

-- 1. 创建 users 表 (用户表)
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

-- 2. 创建 videos 表 (视频表)
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

-- 3. 创建 analyses 表 (分析记录表)
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

-- 完成！现在可以启动后端服务了
