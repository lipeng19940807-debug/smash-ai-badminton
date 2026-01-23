"""
积分服务
处理积分相关的业务逻辑
"""
from typing import Optional, List
from decimal import Decimal
from fastapi import HTTPException, status
from supabase import Client
from app.models.points import PointsTransaction, PurchaseRecord, PurchaseCreate, PointsAdjustRequest


class PointsService:
    """积分服务类"""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def get_user_points(self, user_id: str) -> dict:
        """
        获取用户积分信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户积分信息字典
        """
        try:
            response = self.db.table("users").select(
                "id, username, nickname, points, total_points_earned, total_points_spent, created_at"
            ).eq("id", user_id).execute()
            
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
                detail=f"获取用户积分失败: {str(e)}"
            )
    
    async def adjust_points(
        self, 
        user_id: str, 
        points: int, 
        transaction_type: str,
        description: str,
        related_id: Optional[str] = None,
        related_type: Optional[str] = None
    ) -> dict:
        """
        调整用户积分
        
        Args:
            user_id: 用户ID
            points: 积分数量（正数增加，负数减少）
            transaction_type: 交易类型
            description: 描述
            related_id: 关联ID
            related_type: 关联类型
        
        Returns:
            积分交易记录
        """
        try:
            # 1. 获取当前积分
            user_response = self.db.table("users").select("points, total_points_earned, total_points_spent").eq("id", user_id).execute()
            
            if not user_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )
            
            user = user_response.data[0]
            balance_before = user["points"]
            balance_after = balance_before + points
            
            # 检查余额是否足够（如果是消费）
            if balance_after < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"积分不足，当前余额: {balance_before}，需要: {abs(points)}"
                )
            
            # 2. 更新用户积分
            update_data = {
                "points": balance_after,
                "updated_at": "now()"
            }
            
            if points > 0:
                update_data["total_points_earned"] = user["total_points_earned"] + points
            else:
                update_data["total_points_spent"] = user["total_points_spent"] + abs(points)
            
            self.db.table("users").update(update_data).eq("id", user_id).execute()
            
            # 3. 记录积分交易
            transaction_data = {
                "user_id": user_id,
                "transaction_type": transaction_type,
                "points": points,
                "balance_before": balance_before,
                "balance_after": balance_after,
                "description": description,
                "related_id": related_id,
                "related_type": related_type
            }
            
            transaction_response = self.db.table("points_transactions").insert(transaction_data).execute()
            
            if not transaction_response.data:
                raise Exception("创建积分交易记录失败")
            
            return transaction_response.data[0]
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"调整积分失败: {str(e)}"
            )
    
    async def get_user_transactions(
        self, 
        user_id: str, 
        page: int = 1, 
        page_size: int = 20
    ) -> dict:
        """
        获取用户积分交易记录
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
        
        Returns:
            交易记录列表
        """
        try:
            offset = (page - 1) * page_size
            
            # 查询总数
            count_response = self.db.table("points_transactions").select(
                "id", count="exact"
            ).eq("user_id", user_id).execute()
            
            total = count_response.count if hasattr(count_response, 'count') else len(count_response.data or [])
            
            # 查询记录
            response = self.db.table("points_transactions").select("*").eq(
                "user_id", user_id
            ).order("created_at", desc=True).range(offset, offset + page_size - 1).execute()
            
            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": response.data or []
            }
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取交易记录失败: {str(e)}"
            )
    
    async def create_purchase_record(
        self,
        user_id: str,
        purchase_data: PurchaseCreate,
        payment_method: Optional[str] = None
    ) -> dict:
        """
        创建购买记录
        
        Args:
            user_id: 用户ID
            purchase_data: 购买数据
            payment_method: 支付方式
        
        Returns:
            购买记录
        """
        try:
            record_data = {
                "user_id": user_id,
                "product_type": purchase_data.product_type,
                "product_name": purchase_data.product_name,
                "product_id": purchase_data.product_id,
                "points_amount": purchase_data.points_amount,
                "price": float(purchase_data.price),
                "payment_method": payment_method,
                "payment_status": "pending"
            }
            
            response = self.db.table("purchase_records").insert(record_data).execute()
            
            if not response.data:
                raise Exception("创建购买记录失败")
            
            return response.data[0]
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"创建购买记录失败: {str(e)}"
            )
    
    async def complete_purchase(
        self,
        purchase_id: str,
        payment_transaction_id: Optional[str] = None,
        wechat_order_id: Optional[str] = None
    ) -> dict:
        """
        完成购买（支付成功）
        
        Args:
            purchase_id: 购买记录ID
            payment_transaction_id: 支付交易ID
            wechat_order_id: 微信订单号
        
        Returns:
            更新后的购买记录
        """
        try:
            # 1. 获取购买记录
            purchase_response = self.db.table("purchase_records").select("*").eq("id", purchase_id).execute()
            
            if not purchase_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="购买记录不存在"
                )
            
            purchase = purchase_response.data[0]
            
            if purchase["payment_status"] == "paid":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该订单已支付"
                )
            
            # 2. 更新购买记录状态
            update_data = {
                "payment_status": "paid",
                "paid_at": "now()",
                "updated_at": "now()"
            }
            
            if payment_transaction_id:
                update_data["payment_transaction_id"] = payment_transaction_id
            if wechat_order_id:
                update_data["wechat_order_id"] = wechat_order_id
            
            self.db.table("purchase_records").update(update_data).eq("id", purchase_id).execute()
            
            # 3. 给用户增加积分
            await self.adjust_points(
                user_id=purchase["user_id"],
                points=purchase["points_amount"],
                transaction_type="purchase",
                description=f"购买{purchase['product_name']}",
                related_id=purchase_id,
                related_type="purchase"
            )
            
            # 4. 返回更新后的记录
            updated_response = self.db.table("purchase_records").select("*").eq("id", purchase_id).execute()
            
            return updated_response.data[0]
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"完成购买失败: {str(e)}"
            )
