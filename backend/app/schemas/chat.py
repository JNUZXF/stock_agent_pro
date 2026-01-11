"""
聊天相关Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class ChatRequest(BaseModel):
    """聊天请求Schema"""
    message: str = Field(..., min_length=1, description="用户消息")
    conversation_id: Optional[str] = Field(None, description="会话ID，不提供则创建新会话")
    agent_type: str = Field(default="stock_analysis", description="智能体类型")


class ChatChunkResponse(BaseModel):
    """聊天响应片段Schema（流式输出）"""
    type: Literal["chunk", "done", "error"] = Field(..., description="响应类型")
    content: Optional[str] = Field(None, description="内容片段")
    conversation_id: Optional[str] = Field(None, description="会话ID")
    error: Optional[str] = Field(None, description="错误信息")


class ChatResponse(BaseModel):
    """聊天响应Schema（非流式）"""
    conversation_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="助手回复")
