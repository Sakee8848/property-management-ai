"""
物业管理AI应用 - FastAPI 主应用入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.api import auth, properties, documents, chat, payments, admin
from app.core.config import settings
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 启动物业管理AI应用...")
    await init_db()
    logger.info("✅ 数据库初始化完成")
    
    yield
    
    # 关闭时执行
    logger.info("👋 关闭应用...")


app = FastAPI(
    title="物业管理AI系统API",
    description="智能物业管理平台后端服务",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "property-management-ai",
            "version": "1.0.0"
        }
    )


# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(properties.router, prefix="/api/properties", tags=["物业项目"])
app.include_router(documents.router, prefix="/api/documents", tags=["文档管理"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI聊天"])
app.include_router(payments.router, prefix="/api/payments", tags=["支付管理"])
app.include_router(admin.router, prefix="/api/admin", tags=["系统管理"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用物业管理AI系统",
        "docs": "/api/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
