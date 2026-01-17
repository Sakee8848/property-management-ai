"""
物业项目管理API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import User
from app.models.property import Property, PropertyUnit
from app.api.auth import get_current_user

router = APIRouter()


# Pydantic 模型
class PropertyCreate(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None


class PropertyResponse(BaseModel):
    id: int
    name: str
    code: str
    address: Optional[str]
    city: Optional[str]
    total_units: Optional[int]
    contact_phone: Optional[str]


# API 路由
@router.get("/", response_model=List[PropertyResponse])
async def list_properties(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取物业列表"""
    result = await db.execute(select(Property).where(Property.is_active == 1))
    properties = result.scalars().all()
    
    return [
        PropertyResponse(
            id=prop.id,
            name=prop.name,
            code=prop.code,
            address=prop.address,
            city=prop.city,
            total_units=prop.total_units,
            contact_phone=prop.contact_phone
        )
        for prop in properties
    ]


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取物业详情"""
    result = await db.execute(select(Property).where(Property.id == property_id))
    property = result.scalar_one_or_none()
    
    if not property:
        raise HTTPException(status_code=404, detail="物业不存在")
    
    return PropertyResponse(
        id=property.id,
        name=property.name,
        code=property.code,
        address=property.address,
        city=property.city,
        total_units=property.total_units,
        contact_phone=property.contact_phone
    )
