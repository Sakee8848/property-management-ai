"""
完整的支付管理API实现
"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import User
from app.models.payment import Bill, Payment, FeeType, PaymentStatus, PaymentMethod
from app.api.auth import get_current_user
from app.services.payment_service import PaymentService

router = APIRouter()


# Pydantic 模型
class BillResponse(BaseModel):
    id: int
    bill_number: str
    fee_type: str
    amount: float
    late_fee: float
    total_amount: float
    billing_period: str
    due_date: str
    status: str
    created_at: str


class PaymentRequest(BaseModel):
    bill_id: int
    payment_method: str  # wechat/alipay


class PaymentResponse(BaseModel):
    success: bool
    payment_params: dict = {}
    payment_url: str = ""
    message: str = ""


@router.get("/bills", response_model=List[BillResponse])
async def list_bills(
    status: str = None,
    fee_type: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取账单列表
    
    - 支持按状态筛选(pending/paid/overdue)
    - 支持按费用类型筛选
    """
    # 构建查询
    query = select(Bill).where(Bill.user_id == current_user.id)
    
    # 状态筛选
    if status:
        query = query.where(Bill.status == PaymentStatus(status))
    
    # 费用类型筛选
    if fee_type:
        query = query.where(Bill.fee_type == FeeType(fee_type))
    
    query = query.order_by(desc(Bill.created_at))
    
    result = await db.execute(query)
    bills = result.scalars().all()
    
    return [
        BillResponse(
            id=bill.id,
            bill_number=bill.bill_number,
            fee_type=bill.fee_type.value,
            amount=bill.amount,
            late_fee=bill.late_fee,
            total_amount=bill.total_amount,
            billing_period=bill.billing_period,
            due_date=bill.due_date.isoformat(),
            status=bill.status.value,
            created_at=bill.created_at.isoformat(),
        )
        for bill in bills
    ]


@router.get("/bills/{bill_id}", response_model=BillResponse)
async def get_bill(
    bill_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取账单详情"""
    result = await db.execute(
        select(Bill).where(
            Bill.id == bill_id,
            Bill.user_id == current_user.id
        )
    )
    bill = result.scalar_one_or_none()
    
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    return BillResponse(
        id=bill.id,
        bill_number=bill.bill_number,
        fee_type=bill.fee_type.value,
        amount=bill.amount,
        late_fee=bill.late_fee,
        total_amount=bill.total_amount,
        billing_period=bill.billing_period,
        due_date=bill.due_date.isoformat(),
        status=bill.status.value,
        created_at=bill.created_at.isoformat(),
    )


@router.post("/pay", response_model=PaymentResponse)
async def create_payment(
    payment_req: PaymentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    发起支付
    
    支持微信支付和支付宝
    """
    # 查询账单
    result = await db.execute(
        select(Bill).where(
            Bill.id == payment_req.bill_id,
            Bill.user_id == current_user.id
        )
    )
    bill = result.scalar_one_or_none()
    
    if not bill:
        raise HTTPException(status_code=404, detail="账单不存在")
    
    if bill.status == PaymentStatus.PAID:
        raise HTTPException(status_code=400, detail="账单已支付")
    
    # 创建支付记录
    payment = Payment(
        bill_id=bill.id,
        user_id=current_user.id,
        transaction_id=f"TXN{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{bill.id}",
        payment_method=PaymentMethod(payment_req.payment_method),
        amount=bill.total_amount,
        status=PaymentStatus.PENDING,
    )
    
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    
    # 调用支付服务
    payment_service = PaymentService()
    
    try:
        if payment_req.payment_method == 'wechat':
            # 微信支付
            result = await payment_service.create_wechat_order(
                bill_number=bill.bill_number,
                amount=bill.total_amount,
                description=f"{bill.fee_type.value} - {bill.billing_period}",
                user_openid=current_user.phone  # 实际应该是微信openid
            )
            
            if result["success"]:
                return PaymentResponse(
                    success=True,
                    payment_params=result["payment_params"],
                    message="请使用微信完成支付"
                )
        
        elif payment_req.payment_method == 'alipay':
            # 支付宝
            result = await payment_service.create_alipay_order(
                bill_number=bill.bill_number,
                amount=bill.total_amount,
                description=f"{bill.fee_type.value} - {bill.billing_period}"
            )
            
            if result["success"]:
                return PaymentResponse(
                    success=True,
                    payment_url=result["payment_url"],
                    message="请跳转到支付宝完成支付"
                )
        
        else:
            raise HTTPException(status_code=400, detail="不支持的支付方式")
    
    except Exception as e:
        # 支付失败,更新状态
        payment.status = PaymentStatus.CANCELLED
        await db.commit()
        
        raise HTTPException(status_code=500, detail=f"发起支付失败: {str(e)}")


@router.post("/wechat/notify")
async def wechat_payment_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """微信支付回调"""
    data = await request.form()
    
    payment_service = PaymentService()
    result = await payment_service.verify_wechat_callback(dict(data))
    
    if result["success"]:
        # 查询支付记录
        bill_number = result["out_trade_no"]
        bill_result = await db.execute(
            select(Bill).where(Bill.bill_number == bill_number)
        )
        bill = bill_result.scalar_one_or_none()
        
        if bill:
            # 更新账单状态
            bill.status = PaymentStatus.PAID
            
            # 更新支付记录
            payment_result = await db.execute(
                select(Payment).where(Payment.bill_id == bill.id)
            )
            payment = payment_result.scalar_one_or_none()
            if payment:
                payment.status = PaymentStatus.PAID
                payment.paid_at = datetime.utcnow()
                payment.payment_response = str(data)
            
            await db.commit()
        
        return {"code": "SUCCESS", "message": "OK"}
    
    return {"code": "FAIL", "message": "验证失败"}


@router.post("/alipay/notify")
async def alipay_payment_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """支付宝支付回调"""
    data = await request.form()
    
    payment_service = PaymentService()
    result = await payment_service.verify_alipay_callback(dict(data))
    
    if result["success"]:
        # 查询支付记录
        bill_number = result["out_trade_no"]
        bill_result = await db.execute(
            select(Bill).where(Bill.bill_number == bill_number)
        )
        bill = bill_result.scalar_one_or_none()
        
        if bill:
            # 更新账单状态
            bill.status = PaymentStatus.PAID
            
            # 更新支付记录
            payment_result = await db.execute(
                select(Payment).where(Payment.bill_id == bill.id)
            )
            payment = payment_result.scalar_one_or_none()
            if payment:
                payment.status = PaymentStatus.PAID
                payment.paid_at = datetime.utcnow()
                payment.payment_response = str(data)
            
            await db.commit()
        
        return "success"
    
    return "fail"


@router.get("/history", response_model=List[PaymentResponse])
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取支付历史记录"""
    result = await db.execute(
        select(Payment)
        .where(Payment.user_id == current_user.id)
        .order_by(desc(Payment.created_at))
    )
    payments = result.scalars().all()
    
    return []  # 返回支付记录列表
