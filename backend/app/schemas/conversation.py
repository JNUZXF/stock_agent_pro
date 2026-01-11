"""
对话相关Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MessageBase(BaseModel):
    """消息基础Schema"""
    role: str = Field(..., description="角色: user/assistant/system/tool")
    content: Optional[str] = Field(None, description="消息内容")


class MessageCreate(BaseModel):
    """消息创建Schema"""
    role: str
    content: Optional[str] = None
    function_call: Optional[dict] = None
    tool_calls: Optional[list] = None
    metadata: Optional[dict] = None


class MessageResponse(BaseModel):
    """消息响应Schema"""
    id: int
    role: str
    content: Optional[str]
    function_call: Optional[dict]
    tool_calls: Optional[list]
    message_metadata: Optional[dict] = Field(None, serialization_alias="metadata")
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """对话创建Schema"""
    conversation_id: str = Field(..., description="会话ID")
    title: Optional[str] = Field(None, max_length=200, description="标题")
    summary: Optional[str] = Field(None, description="摘要")


class ConversationUpdate(BaseModel):
    """对话更新Schema"""
    title: Optional[str] = Field(None, max_length=200)
    summary: Optional[str] = None


class ConversationResponse(BaseModel):
    """对话响应Schema"""
    id: int
    conversation_id: str
    title: Optional[str]
    summary: Optional[str]
    message_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationDetail(ConversationResponse):
    """对话详情Schema（包含消息）"""
    messages: List[MessageResponse] = []


class ConversationSummary(BaseModel):
    """对话摘要Schema"""
    id: str = Field(..., description="会话ID")
    title: Optional[str] = Field(None, description="标题")
    date: str = Field(..., description="日期")
    summary: Optional[str] = Field(None, description="摘要")
