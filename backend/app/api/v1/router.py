"""
API v1路由聚合器
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, chat, conversations

# 创建v1路由器
api_router = APIRouter()

# 注册子路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["认证"]
)

api_router.include_router(
    chat.router,
    prefix="",
    tags=["聊天"]
)

api_router.include_router(
    conversations.router,
    prefix="",
    tags=["对话管理"]
)
