"""
Stock Agent Pro - 主应用入口
生产级别的股票分析智能体系统
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging import setup_logging
from app.core.middleware import LoggingMiddleware, ExceptionHandlerMiddleware
from app.db.session import init_db
from app.api.v1.router import api_router

# 初始化日志
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    Args:
        app: FastAPI应用实例
    """
    # 启动时执行
    logger.info(f"=== {settings.APP_NAME} v{settings.APP_VERSION} 启动中 ===")
    logger.info(f"环境: {settings.ENVIRONMENT}")
    logger.info(f"调试模式: {settings.DEBUG}")

    # 初始化数据库
    try:
        init_db()
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise

    # 导入工具以触发注册
    try:
        from app.agents.tools import stock_tool  # noqa
        from app.agents.tools.registry import tool_registry

        logger.info(f"已注册 {tool_registry.count()} 个工具: {tool_registry.get_tool_names()}")
    except Exception as e:
        logger.error(f"工具注册失败: {str(e)}")

    logger.info(f"=== {settings.APP_NAME} 启动完成 ===")

    yield

    # 关闭时执行
    logger.info(f"=== {settings.APP_NAME} 关闭中 ===")

    # 清理智能体管理器
    try:
        from app.agents.manager import agent_manager
        total = agent_manager.get_total_agent_count()
        agent_manager.clear_all()
        logger.info(f"清理 {total} 个智能体实例")
    except Exception as e:
        logger.error(f"清理智能体失败: {str(e)}")

    logger.info(f"=== {settings.APP_NAME} 已关闭 ===")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="生产级别的股票分析智能体系统，支持用户隔离和多版本API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# 添加自定义中间件
app.add_middleware(ExceptionHandlerMiddleware)
app.add_middleware(LoggingMiddleware)

# 注册API路由
app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX
)


@app.get("/")
def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT
    }


@app.get("/health")
def health_check():
    """健康检查"""
    from app.agents.manager import agent_manager

    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": "connected",
        "active_agents": agent_manager.get_total_agent_count()
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
