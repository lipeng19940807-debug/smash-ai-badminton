# 注册失败快速修复指南

## 问题描述

注册时出现错误：`Could not find the 'points' column of 'users' in the schema cache`

这是因为数据库表 `users` 中缺少积分相关字段。

## 解决方案

### 方案1：初始化数据库（推荐）

如果还没有初始化数据库，请执行以下 SQL 脚本：

```sql
-- 在 Supabase SQL Editor 中执行

-- 1. 添加积分字段到 users 表
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS points INTEGER DEFAULT 0 NOT NULL,
ADD COLUMN IF NOT EXISTS total_points_earned INTEGER DEFAULT 0 NOT NULL,
ADD COLUMN IF NOT EXISTS total_points_spent INTEGER DEFAULT 0 NOT NULL;

-- 2. 创建积分交易记录表（如果不存在）
CREATE TABLE IF NOT EXISTS points_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL,
    points INTEGER NOT NULL,
    balance_before INTEGER NOT NULL,
    balance_after INTEGER NOT NULL,
    description TEXT,
    related_id UUID,
    related_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 创建购买记录表（如果不存在）
CREATE TABLE IF NOT EXISTS purchase_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_type VARCHAR(50) NOT NULL,
    product_name VARCHAR(100) NOT NULL,
    product_id VARCHAR(100),
    points_amount INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50),
    payment_status VARCHAR(20) DEFAULT 'pending',
    payment_transaction_id VARCHAR(255),
    wechat_order_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    paid_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 创建触发器：新用户注册时自动赠送50积分
CREATE OR REPLACE FUNCTION give_welcome_points()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE users 
    SET points = points + 50,
        total_points_earned = total_points_earned + 50,
        updated_at = NOW()
    WHERE id = NEW.id;
    
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

DROP TRIGGER IF EXISTS trigger_give_welcome_points ON users;
CREATE TRIGGER trigger_give_welcome_points
    AFTER INSERT ON users
    FOR EACH ROW
    EXECUTE FUNCTION give_welcome_points();
```

### 方案2：使用完整数据库初始化脚本

执行 `backend/database_init_with_points.sql` 文件中的完整脚本。

## 当前代码状态

代码已经更新，现在即使数据库表没有积分字段，注册也能成功。积分功能会在数据库初始化后自动启用。

## 验证修复

1. 执行上述 SQL 脚本
2. 重新尝试注册
3. 检查新用户是否自动获得 50 积分

## 注意事项

- 如果暂时不需要积分功能，可以不执行 SQL 脚本，注册功能仍然可以正常使用
- 积分功能是可选的，不影响核心的注册和登录功能
