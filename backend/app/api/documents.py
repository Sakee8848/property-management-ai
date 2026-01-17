"""
文档管理API
"""
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import User
from app.api.auth import get_current_user

router = APIRouter()


class DocumentResponse(BaseModel):
    id: int
    title: str
    category: str
    file_name: str
    created_at: str


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """上传文档"""
    return {"message": "文档上传功能开发中"}


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取文档列表"""
    return []
