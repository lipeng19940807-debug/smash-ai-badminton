"""
Pydantic 数据模型 - 积分系统
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class PointsTransaction(BaseModel):
    """积分交易记录模型"""
    id: str
    user_id: str
    transaction_type: str  # 'earn', 'spend', 'gift', 'purchase'
    points: int
    balance_before: int
    balance_after: int
    description: Optional[str] = None
    related_id: Optional[str] = None
    related_type: Optional[str] = None
    created_at: datetime


class PurchaseRecord(BaseModel):
    """购买记录模型"""
    id: str
    user_id: str
    product_type: str  # 'points', 'analysis', 'subscription'
    product_name: str
    product_id: Optional[str] = None
    points_amount: int
    price: Decimal
    payment_method: Optional[str] = None  # 'wechat', 'alipay', 'points'
    payment_status: str  # 'pending', 'paid', 'failed', 'refunded'
    payment_transaction_id: Optional[str] = None
    wechat_order_id: Optional[str] = None
    created_at: datetime
    paid_at: Optional[datetime] = None
    updated_at: datetime


class PurchaseCreate(BaseModel):
    """创建购买记录请求"""
    product_type: str = Field(..., description="产品类型")
    product_name: str = Field(..., description="产品名称")
    product_id: Optional[str] = None
    points_amount: int = Field(..., gt=0, description="积分数量")
    price: Decimal = Field(..., ge=0, description="价格")


class PointsAdjustRequest(BaseModel):
    """积分调整请求（管理员）"""
    user_id: str
    points: int = Field(..., description="积分数量（正数增加，负数减少）")
    description: str = Field(..., description="调整原因")
    transaction_type: str = Field(default="gift", description="交易类型")


class UserPointsInfo(BaseModel):
    """用户积分信息"""
    user_id: str
    username: str
    nickname: Optional[str] = None
    points: int
    total_points_earned: int
    total_points_spent: int
    created_at: datetime
