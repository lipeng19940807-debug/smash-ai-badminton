-- 羽毛球杀球分析系统 - 数据库初始化脚本（包含积分系统）
-- 在 Supabase SQL Editor 中执行此脚本

-- 1. 创建 users 表 (用户表) - 添加积分字段
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    avatar_url TEXT,
    points INTEGER DEFAULT 0 NOT NULL,  -- 用户积分
    total_points_earned INTEGER DEFAULT 0 NOT NULL,  -- 累计获得积分
    total_points_spent INTEGER DEFAULT 0 NOT NULL,  -- 累计消费积分
    wechat_openid VARCHAR(100) UNIQUE,  -- 微信 OpenID
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_wechat_openid ON users(wechat_openid);
CREATE INDEX IF NOT EXISTS idx_users_points ON users(points DESC);

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
    points_cost INTEGER DEFAULT 10 NOT NULL,  -- 本次分析消耗的积分
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    analysis_duration FLOAT
);

CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_video_id ON analyses(video_id);
CREATE INDEX IF NOT EXISTS idx_analyses_analyzed_at ON analyses(analyzed_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_speed ON analyses(speed DESC);

-- 4. 创建 points_transactions 表 (积分交易记录表)
CREATE TABLE IF NOT EXISTS points_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL,  -- 'earn' 获得, 'spend' 消费, 'gift' 赠送, 'purchase' 购买
    points INTEGER NOT NULL,  -- 积分数量（正数表示获得，负数表示消费）
    balance_before INTEGER NOT NULL,  -- 交易前余额
    balance_after INTEGER NOT NULL,  -- 交易后余额
    description TEXT,  -- 交易描述
    related_id UUID,  -- 关联ID（如购买记录ID、分析记录ID等）
    related_type VARCHAR(50),  -- 关联类型（如 'purchase', 'analysis', 'gift'）
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_points_transactions_user_id ON points_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_points_transactions_type ON points_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_points_transactions_created_at ON points_transactions(created_at DESC);

-- 5. 创建 purchase_records 表 (购买记录表)
CREATE TABLE IF NOT EXISTS purchase_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_type VARCHAR(50) NOT NULL,  -- 'points' 积分包, 'analysis' 单次分析, 'subscription' 订阅等
    product_name VARCHAR(100) NOT NULL,  -- 产品名称
    product_id VARCHAR(100),  -- 产品ID
    points_amount INTEGER NOT NULL,  -- 获得的积分数量
    price DECIMAL(10, 2) NOT NULL,  -- 价格（元）
    payment_method VARCHAR(50),  -- 支付方式：'wechat', 'alipay', 'points' 等
    payment_status VARCHAR(20) DEFAULT 'pending',  -- 'pending', 'paid', 'failed', 'refunded'
    payment_transaction_id VARCHAR(255),  -- 支付交易ID
    wechat_order_id VARCHAR(255),  -- 微信订单号
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    paid_at TIMESTAMP WITH TIME ZONE,  -- 支付时间
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_purchase_records_user_id ON purchase_records(user_id);
CREATE INDEX IF NOT EXISTS idx_purchase_records_status ON purchase_records(payment_status);
CREATE INDEX IF NOT EXISTS idx_purchase_records_created_at ON purchase_records(created_at DESC);

-- 6. 创建 admin_users 表 (管理员用户表)
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    role VARCHAR(20) DEFAULT 'admin',  -- 'admin' 管理员, 'super_admin' 超级管理员
    is_active BOOLEAN DEFAULT TRUE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_admin_users_username ON admin_users(username);
CREATE INDEX IF NOT EXISTS idx_admin_users_role ON admin_users(role);

-- 7. 为新注册用户添加积分的函数
CREATE OR REPLACE FUNCTION give_welcome_points()
RETURNS TRIGGER AS $$
BEGIN
    -- 新用户注册时赠送 50 积分
    UPDATE users 
    SET points = points + 50,
        total_points_earned = total_points_earned + 50,
        updated_at = NOW()
    WHERE id = NEW.id;
    
    -- 记录积分交易
    INSERT INTO points_transactions (
        user_id, 
        transaction_type, 
        points, 
        balance_before, 
        balance_after, 
        description,
        related_type
    ) VALUES (
        NEW.id,
        'gift',
        50,
        0,
        50,
        '新用户注册奖励',
        'welcome_bonus'
    );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器：新用户注册时自动赠送积分
DROP TRIGGER IF EXISTS trigger_give_welcome_points ON users;
CREATE TRIGGER trigger_give_welcome_points
    AFTER INSERT ON users
    FOR EACH ROW
    EXECUTE FUNCTION give_welcome_points();

-- 完成！现在可以启动后端服务了
