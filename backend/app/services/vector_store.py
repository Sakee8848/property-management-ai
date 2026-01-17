"""
向量存储服务 - 用于RAG检索
"""
from typing import List, Dict, Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from loguru import logger

from app.core.config import settings


class VectorStoreService:
    """向量存储服务类"""
    
    def __init__(self, property_id: int):
        self.property_id = property_id
        self.collection_name = f"{settings.VECTOR_COLLECTION_NAME}_{property_id}"
        self.client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None
        )
        self.encoder = SentenceTransformer(
            'paraphrase-multilingual-MiniLM-L12-v2'  # 支持中文的模型
        )
    
    async def init_collection(self):
        """初始化集合"""
        try:
            collections = await self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                await self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,  # MiniLM模型的向量维度
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"创建向量集合: {self.collection_name}")
        
        except Exception as e:
            logger.error(f"初始化集合错误: {str(e)}")
    
    async def add_document(
        self,
        document_id: int,
        title: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        添加文档到向量存储
        
        Args:
            document_id: 文档ID
            title: 文档标题
            content: 文档内容
            metadata: 额外的元数据
        """
        try:
            await self.init_collection()
            
            # 分块处理长文档
            chunks = self._split_text(content)
            
            points = []
            for i, chunk in enumerate(chunks):
                # 生成向量
                text = f"{title}\n\n{chunk}"
                vector = self.encoder.encode(text).tolist()
                
                # 创建点
                point_id = f"{document_id}_{i}"
                payload = {
                    "document_id": document_id,
                    "title": title,
                    "content": chunk,
                    "chunk_index": i,
                    "property_id": self.property_id,
                }
                if metadata:
                    payload.update(metadata)
                
                points.append(PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=payload
                ))
            
            # 批量插入
            await self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"添加文档到向量库: document_id={document_id}, chunks={len(chunks)}")
        
        except Exception as e:
            logger.error(f"添加文档到向量库错误: {str(e)}")
    
    async def search(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.5
    ) -> List[Dict]:
        """
        搜索相关文档
        
        Args:
            query: 查询文本
            limit: 返回结果数量
            score_threshold: 相似度阈值
        
        Returns:
            相关文档列表
        """
        try:
            # 生成查询向量
            query_vector = self.encoder.encode(query).tolist()
            
            # 搜索
            results = await self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )
            
            # 格式化结果
            documents = []
            for result in results:
                documents.append({
                    "id": result.payload["document_id"],
                    "title": result.payload["title"],
                    "content": result.payload["content"],
                    "score": result.score,
                })
            
            return documents
        
        except Exception as e:
            logger.error(f"搜索向量库错误: {str(e)}")
            return []
    
    async def delete_document(self, document_id: int):
        """删除文档"""
        try:
            await self.client.delete(
                collection_name=self.collection_name,
                points_selector={
                    "filter": {
                        "must": [
                            {
                                "key": "document_id",
                                "match": {"value": document_id}
                            }
                        ]
                    }
                }
            )
            logger.info(f"从向量库删除文档: document_id={document_id}")
        
        except Exception as e:
            logger.error(f"删除向量库文档错误: {str(e)}")
    
    def _split_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """
        分割文本为块
        
        Args:
            text: 原始文本
            chunk_size: 每块的大小(字符数)
        
        Returns:
            文本块列表
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
        
        return chunks
