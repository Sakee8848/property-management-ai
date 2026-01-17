"""
AI聊天API路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel

from app.db.database import get_db
from app.models.user import User
from app.models.message import Conversation, Message, MessageRole, ConversationStatus
from app.api.auth import get_current_user
from app.services.ai_service import AIService

router = APIRouter()


# Pydantic 模型
class ChatMessage(BaseModel):
    content: str
    conversation_id: Optional[int] = None


class MessageResponse(BaseModel):
    id: int
    role: MessageRole
    content: str
    sources: List[dict] = []
    created_at: str


class ConversationResponse(BaseModel):
    id: int
    title: Optional[str]
    status: ConversationStatus
    message_count: int
    last_message_at: str
    messages: List[MessageResponse] = []


# API 路由
@router.post("/send", response_model=MessageResponse)
async def send_message(
    message_data: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """发送消息并获取AI回复"""
    
    # 如果没有指定会话,创建新会话
    if not message_data.conversation_id:
        new_conversation = Conversation(
            user_id=current_user.id,
            property_id=current_user.property_id,
            title=message_data.content[:50],  # 使用消息开头作为标题
        )
        db.add(new_conversation)
        await db.commit()
        await db.refresh(new_conversation)
        conversation_id = new_conversation.id
    else:
        conversation_id = message_data.conversation_id
        # 验证会话是否属于当前用户
        result = await db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == current_user.id
            )
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise HTTPException(status_code=404, detail="会话不存在")
    
    # 保存用户消息
    user_message = Message(
        conversation_id=conversation_id,
        role=MessageRole.USER,
        content=message_data.content,
    )
    db.add(user_message)
    await db.commit()
    
    # 获取AI回复
    ai_service = AIService(db, current_user.property_id)
    ai_response = await ai_service.chat(
        conversation_id=conversation_id,
        user_message=message_data.content
    )
    
    # 保存AI消息
    assistant_message = Message(
        conversation_id=conversation_id,
        role=MessageRole.ASSISTANT,
        content=ai_response["content"],
        model=ai_response.get("model"),
        tokens=ai_response.get("tokens"),
        sources=ai_response.get("sources", []),
    )
    db.add(assistant_message)
    
    # 更新会话统计
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one()
    conversation.message_count += 2
    
    await db.commit()
    await db.refresh(assistant_message)
    
    return MessageResponse(
        id=assistant_message.id,
        role=assistant_message.role,
        content=assistant_message.content,
        sources=assistant_message.sources,
        created_at=assistant_message.created_at.isoformat(),
    )


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户的所有会话"""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(desc(Conversation.last_message_at))
    )
    conversations = result.scalars().all()
    
    response = []
    for conv in conversations:
        response.append(ConversationResponse(
            id=conv.id,
            title=conv.title,
            status=conv.status,
            message_count=conv.message_count,
            last_message_at=conv.last_message_at.isoformat(),
            messages=[],
        ))
    
    return response


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取会话详情和消息历史"""
    # 验证会话
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 获取消息
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    
    message_list = [
        MessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            sources=msg.sources,
            created_at=msg.created_at.isoformat(),
        )
        for msg in messages
    ]
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        status=conversation.status,
        message_count=conversation.message_count,
        last_message_at=conversation.last_message_at.isoformat(),
        messages=message_list,
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除会话"""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="会话不存在")
    
    # 删除相关消息
    await db.execute(
        select(Message).where(Message.conversation_id == conversation_id)
    )
    
    await db.delete(conversation)
    await db.commit()
    
    return {"message": "会话已删除"}
