"""
用户相关Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础Schema"""
    username: str
    email: EmailStr


class UserCreate(BaseModel):
    """用户创建Schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    is_superuser: bool = False


class UserUpdate(BaseModel):
    """用户更新Schema"""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    max_conversations: Optional[int] = None
    max_messages_per_conversation: Optional[int] = None


class UserResponse(BaseModel):
    """用户响应Schema"""
    id: int
    username: str
    email: str
    is_active: bool
    is_superuser: bool
    max_conversations: int
    max_messages_per_conversation: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """用户档案Schema"""
    id: int
    username: str
    email: str
    is_active: bool
    max_conversations: int
    max_messages_per_conversation: int
    conversation_count: int = 0

    class Config:
        from_attributes = True
