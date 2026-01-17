"""
物业项目模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.orm import relationship

from app.db.database import Base


class Property(Base):
    """物业项目表"""
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    
    # 基本信息
    address = Column(String(500))
    city = Column(String(100))
    province = Column(String(100))
    postal_code = Column(String(20))
    
    description = Column(Text)
    total_area = Column(Float)  # 总建筑面积
    total_units = Column(Integer)  # 总户数
    
    # 联系信息
    contact_phone = Column(String(50))
    contact_email = Column(String(100))
    office_hours = Column(String(200))
    
    # 物业管理公司信息
    management_company = Column(String(200))
    
    # 配置信息 (JSON格式存储各种设置)
    config = Column(JSON, default={})
    
    # 状态
    is_active = Column(Integer, default=1)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Property(id={self.id}, name={self.name}, code={self.code})>"


class PropertyUnit(Base):
    """物业单元表(房屋/商铺)"""
    __tablename__ = "property_units"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, nullable=False, index=True)
    
    # 单元信息
    building = Column(String(50))  # 楼栋号
    unit = Column(String(50))      # 单元号
    floor = Column(String(20))     # 楼层
    room = Column(String(50))      # 门牌号
    
    # 面积和类型
    area = Column(Float)  # 建筑面积
    unit_type = Column(String(50))  # 类型: 住宅/商铺/办公等
    
    # 业主信息
    owner_id = Column(Integer, nullable=True)  # 关联用户ID
    owner_name = Column(String(100))
    owner_phone = Column(String(20))
    
    # 状态
    is_occupied = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<PropertyUnit(id={self.id}, building={self.building}, room={self.room})>"
