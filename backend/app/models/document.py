"""
文档管理模型
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, JSON

from app.db.database import Base


class DocumentCategory(str, Enum):
    """文档分类"""
    REGULATION = "regulation"          # 物业规章制度
    NOTICE = "notice"                  # 通知公告
    MAINTENANCE = "maintenance"        # 维修记录
    MEETING = "meeting"                # 会议记录
    CONTRACT = "contract"              # 合同协议
    FINANCIAL = "financial"            # 财务报表
    COMPLAINT = "complaint"            # 投诉记录
    FACILITY = "facility"              # 设施设备
    SAFETY = "safety"                  # 安全管理
    OTHER = "other"                    # 其他


class Document(Base):
    """文档表"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, nullable=False, index=True)
    
    # 文档基本信息
    title = Column(String(500), nullable=False)
    category = Column(SQLEnum(DocumentCategory), default=DocumentCategory.OTHER)
    
    # 文件信息
    file_name = Column(String(500))
    file_path = Column(String(1000))
    file_type = Column(String(50))  # pdf, docx, xlsx, etc.
    file_size = Column(Integer)     # 文件大小(字节)
    
    # 内容
    content = Column(Text)  # 提取的文本内容
    summary = Column(Text)  # AI生成的摘要
    
    # 向量化信息
    vector_id = Column(String(100))  # 向量数据库中的ID
    embeddings_generated = Column(Integer, default=0)
    
    # 标签和元数据
    tags = Column(JSON, default=[])
    metadata = Column(JSON, default={})
    
    # 上传者信息
    uploaded_by = Column(Integer)  # 用户ID
    
    # 状态
    is_processed = Column(Integer, default=0)  # 是否已处理
    is_public = Column(Integer, default=1)     # 是否公开
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Document(id={self.id}, title={self.title}, category={self.category})>"
