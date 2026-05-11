#!/usr/bin/env python3
"""
DevCollab 后端主入口

FastAPI应用入口点，包含API路由、中间件、事件处理等。
"""

import os
import logging
from typing import Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field

from app.api import router as api_router
from app.core.state_manager import StateManager
from app.core.orchestrator import Orchestrator
from app.memory.memory_manager import MemoryManager
from app.tools.tool_registry import ToolRegistry

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/app.log")
    ]
)
logger = logging.getLogger(__name__)


class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="API版本")
    timestamp: str = Field(..., description="当前时间戳")
    services: Dict[str, str] = Field(..., description="各服务状态")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    Args:
        app: FastAPI应用实例
    """
    # 启动时初始化
    logger.info("启动 DevCollab 后端服务...")
    
    # 初始化核心组件
    try:
        # 初始化工具注册表
        app.state.tool_registry = ToolRegistry()
        logger.info("工具注册表初始化完成")
        
        # 初始化记忆管理器
        app.state.memory_manager = MemoryManager()
        logger.info("记忆管理器初始化完成")
        
        # 初始化状态管理器
        app.state.state_manager = StateManager()
        logger.info("状态管理器初始化完成")
        
        # 初始化工作流编排器
        app.state.orchestrator = Orchestrator(
            tool_registry=app.state.tool_registry,
            memory_manager=app.state.memory_manager,
            state_manager=app.state.state_manager
        )
        logger.info("工作流编排器初始化完成")
        
        # 注册工具
        await app.state.tool_registry.register_all_tools()
        logger.info("工具注册完成")
        
        # 连接数据库
        await app.state.memory_manager.connect()
        logger.info("数据库连接成功")
        
        logger.info("DevCollab 后端服务启动完成")
        
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise
    
    yield
    
    # 关闭时清理
    logger.info("关闭 DevCollab 后端服务...")
    
    try:
        # 断开数据库连接
        await app.state.memory_manager.disconnect()
        logger.info("数据库连接已关闭")
        
        # 清理资源
        await app.state.orchestrator.cleanup()
        logger.info("工作流编排器已清理")
        
    except Exception as e:
        logger.error(f"服务关闭时发生错误: {e}")
    
    logger.info("DevCollab 后端服务已关闭")


# 创建FastAPI应用
app = FastAPI(
    title="DevCollab API",
    description="多Agent协作智能软件开发助手系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加自定义中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    logger.info(f"收到请求: {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        logger.info(f"请求完成: {request.method} {request.url.path} - 状态码: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"请求处理失败: {request.method} {request.url.path} - 错误: {e}")
        raise


# 异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": request.url.path
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常处理"""
    logger.error(f"请求验证失败: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "请求数据验证失败",
            "details": exc.errors(),
            "path": request.url.path
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "服务器内部错误",
            "message": str(exc),
            "path": request.url.path
        }
    )


# 健康检查端点
@app.get("/health", response_model=HealthCheckResponse, tags=["系统"])
async def health_check():
    """
    健康检查端点
    
    返回服务状态和版本信息
    """
    from datetime import datetime
    
    # 检查各组件状态
    services = {
        "api": "healthy",
        "database": "healthy" if hasattr(app.state, 'memory_manager') and app.state.memory_manager.is_connected() else "unhealthy",
        "redis": "healthy",  # 实际应检查Redis连接
        "milvus": "healthy",  # 实际应检查Milvus连接
        "orchestrator": "healthy" if hasattr(app.state, 'orchestrator') else "unhealthy"
    }
    
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        services=services
    )


@app.get("/", tags=["系统"])
async def root():
    """
    根端点
    
    返回API基本信息
    """
    return {
        "name": "DevCollab API",
        "description": "多Agent协作智能软件开发助手系统",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# 包含API路由
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    
    # 从环境变量获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("DEBUG", "false").lower() == "true"
    
    # 创建日志目录
    os.makedirs("logs", exist_ok=True)
    
    logger.info(f"启动服务器: {host}:{port} (reload={reload})")
    
    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )