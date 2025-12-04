# backend/api/models.py
# API请求和响应的Pydantic模型定义

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str = Field(..., description="用户消息内容", min_length=1)
    conversation_id: Optional[str] = Field(None, description="会话ID，不提供则创建新会话")


class ChatChunkResponse(BaseModel):
    """流式响应数据块模型"""
    type: str = Field(..., description="响应类型: chunk|done|error")
    content: Optional[str] = Field(None, description="内容片段")
    conversation_id: Optional[str] = Field(None, description="会话ID")
    error: Optional[str] = Field(None, description="错误信息")


class ConversationSummary(BaseModel):
    """会话摘要模型"""
    id: str
    title: str
    date: str
    summary: str


class ConversationsResponse(BaseModel):
    """会话列表响应模型"""
    conversations: List[ConversationSummary]


class Message(BaseModel):
    """消息模型"""
    role: str = Field(..., description="角色: user|assistant|system")
    content: str = Field(..., description="消息内容")


class ConversationDetail(BaseModel):
    """会话详情模型"""
    id: str
    messages: List[Message]


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: Dict[str, Any]

