"""
支付管理API
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter()


class BillResponse(BaseModel):
    id: int
    bill_number: str
    fee_type: str
    amount: float
    status: str


@router.get("/bills", response_model=List[BillResponse])
async def list_bills(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取账单列表"""
    return []


@router.post("/pay/{bill_id}")
async def pay_bill(
    bill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """支付账单"""
    return {"message": "支付功能开发中"}
