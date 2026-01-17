"""
完整的文档管理API实现
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import User
from app.models.document import Document, DocumentCategory
from app.api.auth import get_current_user
from app.services.document_service import DocumentProcessor
from app.services.ai_service import AIService
from app.services.vector_store import VectorStoreService

router = APIRouter()


# Pydantic 模型
class DocumentResponse(BaseModel):
    id: int
    title: str
    category: str
    file_name: str
    file_type: str
    file_size: int
    summary: Optional[str]
    is_processed: bool
    created_at: str


class DocumentDetailResponse(DocumentResponse):
    content: Optional[str]
    tags: List[str] = []
    metadata: dict = {}


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    上传文档
    
    - 支持多种格式: PDF, Word, Excel, 图片, 文本
    - 自动提取文本内容
    - AI自动分类和生成摘要
    - 向量化存储以支持语义搜索
    """
    if not current_user.property_id:
        raise HTTPException(status_code=400, detail="用户未关联物业")
    
    # 检查文件类型
    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    allowed_extensions = [ext.lstrip('.') for ext in settings.ALLOWED_EXTENSIONS]
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_ext}")
    
    # 保存文件
    processor = DocumentProcessor()
    file_info = await processor.save_file(file.file, file.filename, current_user.property_id)
    
    # 创建文档记录
    document = Document(
        property_id=current_user.property_id,
        title=title or file.filename,
        file_name=file_info["file_name"],
        file_path=file_info["file_path"],
        file_type=file_info["file_type"],
        file_size=file_info["file_size"],
        uploaded_by=current_user.id,
        is_processed=0,
    )
    
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    # 异步处理文档(提取文本、分类、生成摘要、向量化)
    # 在实际生产环境中,这部分应该放到Celery任务中
    try:
        # 提取文本
        content = processor.extract_text(file_info["file_path"], file_info["file_type"])
        document.content = content[:10000]  # 限制长度
        
        # AI处理
        ai_service = AIService(db, current_user.property_id)
        
        # 自动分类
        if not category:
            detected_category = await ai_service.classify_document(
                title=document.title,
                content=content[:1000]
            )
            document.category = DocumentCategory(detected_category)
        else:
            document.category = DocumentCategory(category)
        
        # 生成摘要
        if content:
            summary = await ai_service.generate_summary(content)
            document.summary = summary
        
        # 向量化存储
        if content:
            vector_store = VectorStoreService(current_user.property_id)
            await vector_store.add_document(
                document_id=document.id,
                title=document.title,
                content=content,
                metadata={
                    "category": document.category.value,
                    "file_type": document.file_type,
                }
            )
            document.embeddings_generated = 1
        
        document.is_processed = 1
        await db.commit()
    
    except Exception as e:
        logger.error(f"处理文档错误: {str(e)}")
        # 即使处理失败,文档也已上传
    
    return DocumentResponse(
        id=document.id,
        title=document.title,
        category=document.category.value,
        file_name=document.file_name,
        file_type=document.file_type,
        file_size=document.file_size,
        summary=document.summary,
        is_processed=bool(document.is_processed),
        created_at=document.created_at.isoformat(),
    )


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取文档列表
    
    - 支持按分类筛选
    - 支持关键词搜索
    """
    if not current_user.property_id:
        raise HTTPException(status_code=400, detail="用户未关联物业")
    
    # 构建查询
    query = select(Document).where(
        Document.property_id == current_user.property_id,
        Document.is_public == 1
    )
    
    # 分类筛选
    if category:
        query = query.where(Document.category == DocumentCategory(category))
    
    # 关键词搜索
    if search:
        query = query.where(
            (Document.title.ilike(f"%{search}%")) |
            (Document.content.ilike(f"%{search}%"))
        )
    
    query = query.order_by(desc(Document.created_at))
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return [
        DocumentResponse(
            id=doc.id,
            title=doc.title,
            category=doc.category.value,
            file_name=doc.file_name,
            file_type=doc.file_type,
            file_size=doc.file_size,
            summary=doc.summary,
            is_processed=bool(doc.is_processed),
            created_at=doc.created_at.isoformat(),
        )
        for doc in documents
    ]


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取文档详情"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.property_id == current_user.property_id
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    return DocumentDetailResponse(
        id=document.id,
        title=document.title,
        category=document.category.value,
        file_name=document.file_name,
        file_type=document.file_type,
        file_size=document.file_size,
        summary=document.summary,
        content=document.content,
        tags=document.tags,
        metadata=document.metadata,
        is_processed=bool(document.is_processed),
        created_at=document.created_at.isoformat(),
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除文档"""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.property_id == current_user.property_id
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 删除文件
    processor = DocumentProcessor()
    processor.delete_file(document.file_path)
    
    # 删除向量
    vector_store = VectorStoreService(current_user.property_id)
    await vector_store.delete_document(document_id)
    
    # 删除记录
    await db.delete(document)
    await db.commit()
    
    return {"message": "文档已删除"}


@router.get("/search/semantic")
async def semantic_search(
    query: str,
    limit: int = 5,
    current_user: User = Depends(get_current_user),
):
    """
    语义搜索
    
    使用向量相似度搜索相关文档
    """
    if not current_user.property_id:
        raise HTTPException(status_code=400, detail="用户未关联物业")
    
    vector_store = VectorStoreService(current_user.property_id)
    results = await vector_store.search(query=query, limit=limit)
    
    return {
        "query": query,
        "results": results
    }
