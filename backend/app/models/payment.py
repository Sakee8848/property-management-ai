"""
支付和费用模型
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum, Text

from app.db.database import Base


class FeeType(str, Enum):
    """费用类型"""
    PROPERTY = "property"        # 物业费
    WATER = "water"              # 水费
    ELECTRICITY = "electricity"  # 电费
    GAS = "gas"                  # 燃气费
    HEATING = "heating"          # 供暖费
    PARKING = "parking"          # 停车费
    MAINTENANCE = "maintenance"  # 维修费
    OTHER = "other"              # 其他


class PaymentStatus(str, Enum):
    """支付状态"""
    PENDING = "pending"      # 待支付
    PAID = "paid"            # 已支付
    OVERDUE = "overdue"      # 逾期
    CANCELLED = "cancelled"  # 已取消
    REFUNDED = "refunded"    # 已退款


class PaymentMethod(str, Enum):
    """支付方式"""
    WECHAT = "wechat"        # 微信支付
    ALIPAY = "alipay"        # 支付宝
    BANK = "bank"            # 银行转账
    CASH = "cash"            # 现金
    OTHER = "other"          # 其他


class Bill(Base):
    """账单表"""
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, nullable=False, index=True)
    unit_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # 账单信息
    bill_number = Column(String(100), unique=True, nullable=False, index=True)
    fee_type = Column(SQLEnum(FeeType), nullable=False)
    
    # 金额
    amount = Column(Float, nullable=False)
    late_fee = Column(Float, default=0.0)  # 滞纳金
    total_amount = Column(Float, nullable=False)
    
    # 账期
    billing_period = Column(String(50))  # 例如: 2024-01
    due_date = Column(DateTime, nullable=False)
    
    # 状态
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # 描述
    description = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Bill(id={self.id}, bill_number={self.bill_number}, status={self.status})>"


class Payment(Base):
    """支付记录表"""
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # 支付信息
    transaction_id = Column(String(200), unique=True, index=True)  # 第三方交易号
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    
    # 金额
    amount = Column(Float, nullable=False)
    
    # 状态
    status = Column(SQLEnum(PaymentStatus), nullable=False)
    
    # 第三方响应
    payment_response = Column(Text)
    
    # 时间戳
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Payment(id={self.id}, transaction_id={self.transaction_id}, status={self.status})>"
