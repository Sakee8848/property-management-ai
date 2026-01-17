"""
聊天消息模型
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, JSON

from app.db.database import Base


class MessageRole(str, Enum):
    """消息角色"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationStatus(str, Enum):
    """对话状态"""
    ACTIVE = "active"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Conversation(Base):
    """对话会话表"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    property_id = Column(Integer, nullable=False, index=True)
    
    # 会话信息
    title = Column(String(500))  # 对话标题(自动生成)
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE)
    
    # 统计信息
    message_count = Column(Integer, default=0)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title}, status={self.status})>"


class Message(Base):
    """消息表"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, nullable=False, index=True)
    
    # 消息内容
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    
    # AI相关信息
    model = Column(String(100))  # 使用的模型
    tokens = Column(Integer)     # 使用的token数
    
    # 引用的文档(RAG检索结果)
    sources = Column(JSON, default=[])
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"
