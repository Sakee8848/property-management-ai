"""
AI服务模块 - 集成LLM和RAG
"""
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from openai import AsyncOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger

from app.core.config import settings
from app.models.message import Message, MessageRole
from app.services.vector_store import VectorStoreService


class AIService:
    """AI服务类"""
    
    def __init__(self, db: AsyncSession, property_id: int):
        self.db = db
        self.property_id = property_id
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.vector_store = VectorStoreService(property_id)
    
    async def chat(
        self,
        conversation_id: int,
        user_message: str,
        use_rag: bool = True
    ) -> Dict:
        """
        处理聊天消息
        
        Args:
            conversation_id: 会话ID
            user_message: 用户消息
            use_rag: 是否使用RAG检索
        
        Returns:
            包含回复内容和元数据的字典
        """
        try:
            # 获取历史消息
            history = await self._get_conversation_history(conversation_id, limit=10)
            
            # 构建消息列表
            messages = [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                }
            ]
            
            # 如果启用RAG,检索相关文档
            sources = []
            if use_rag:
                retrieved_docs = await self.vector_store.search(
                    query=user_message,
                    limit=3
                )
                
                if retrieved_docs:
                    context = self._format_context(retrieved_docs)
                    messages.append({
                        "role": "system",
                        "content": f"以下是相关的物业文档信息:\n\n{context}\n\n请基于这些信息回答用户的问题。"
                    })
                    sources = [
                        {
                            "document_id": doc["id"],
                            "title": doc["title"],
                            "score": doc["score"]
                        }
                        for doc in retrieved_docs
                    ]
            
            # 添加历史消息
            messages.extend(history)
            
            # 添加当前用户消息
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # 调用LLM
            response = await self.client.chat.completions.create(
                model=settings.DEFAULT_AI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
            )
            
            assistant_message = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return {
                "content": assistant_message,
                "model": settings.DEFAULT_AI_MODEL,
                "tokens": tokens_used,
                "sources": sources,
            }
        
        except Exception as e:
            logger.error(f"AI聊天错误: {str(e)}")
            return {
                "content": "抱歉,我现在遇到了一些问题。请稍后再试。",
                "model": settings.DEFAULT_AI_MODEL,
                "tokens": 0,
                "sources": [],
            }
    
    async def _get_conversation_history(
        self,
        conversation_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """获取对话历史"""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        
        # 转换为API格式(注意要反转顺序)
        history = []
        for msg in reversed(messages):
            if msg.role in [MessageRole.USER, MessageRole.ASSISTANT]:
                history.append({
                    "role": msg.role.value,
                    "content": msg.content
                })
        
        return history
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的物业管理AI助手,名字叫"小管家"。你的职责是:

1. 友好、专业地回答业主关于物业服务的各种问题
2. 提供准确的物业规定、流程和服务信息
3. 协助处理报修、投诉、咨询等事务
4. 如果不确定答案,诚实地告知并建议联系物业人员

回答要求:
- 使用礼貌、专业的语言
- 回答简洁明了,重点突出
- 如果有相关文档信息,优先基于文档回答
- 对于需要人工处理的事务,主动引导用户联系物业
"""
    
    def _format_context(self, documents: List[Dict]) -> str:
        """格式化检索到的文档上下文"""
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(
                f"文档{i}: {doc['title']}\n"
                f"内容: {doc['content']}\n"
            )
        return "\n".join(context_parts)
    
    async def generate_summary(self, text: str) -> str:
        """生成文本摘要"""
        try:
            response = await self.client.chat.completions.create(
                model=settings.DEFAULT_AI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的文档摘要助手。请为以下文本生成简洁的摘要,突出关键信息。"
                    },
                    {
                        "role": "user",
                        "content": text[:4000]  # 限制长度
                    }
                ],
                temperature=0.5,
                max_tokens=300,
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"生成摘要错误: {str(e)}")
            return ""
    
    async def classify_document(self, title: str, content: str) -> str:
        """智能分类文档"""
        categories = {
            "regulation": "物业规章制度",
            "notice": "通知公告",
            "maintenance": "维修记录",
            "meeting": "会议记录",
            "contract": "合同协议",
            "financial": "财务报表",
            "complaint": "投诉记录",
            "facility": "设施设备",
            "safety": "安全管理",
            "other": "其他"
        }
        
        categories_str = "\n".join([f"{k}: {v}" for k, v in categories.items()])
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.DEFAULT_AI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": f"你是一个文档分类助手。请根据文档标题和内容,选择最合适的分类。\n\n可选分类:\n{categories_str}\n\n只需返回分类的英文代码(如:regulation)。"
                    },
                    {
                        "role": "user",
                        "content": f"标题: {title}\n内容: {content[:500]}"
                    }
                ],
                temperature=0.3,
                max_tokens=20,
            )
            
            category = response.choices[0].message.content.strip().lower()
            if category in categories:
                return category
            return "other"
        
        except Exception as e:
            logger.error(f"分类文档错误: {str(e)}")
            return "other"
