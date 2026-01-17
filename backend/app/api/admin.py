"""
系统管理API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取系统统计信息"""
    return {
        "total_users": 0,
        "total_properties": 0,
        "total_documents": 0,
    }
