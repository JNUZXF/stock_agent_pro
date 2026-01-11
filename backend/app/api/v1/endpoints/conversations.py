"""
对话管理API端点
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.conversation_service import ConversationService
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationDetail,
    ConversationUpdate,
    ConversationSummary,
    MessageResponse
)
from app.core.security import get_current_user_id_or_default
from app.core.exceptions import ResourceNotFoundError, AuthorizationError

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conversation_data: ConversationCreate,
    user_id: str = Depends(get_current_user_id_or_default),
    db: Session = Depends(get_db)
):
    """
    创建新对话

    Args:
        conversation_data: 对话数据
        user_id: 用户ID（从Token获取）
        db: 数据库会话

    Returns:
        创建的对话
    """
    try:
        conversation_service = ConversationService(db)
        conversation = conversation_service.create_conversation(
            user_id=int(user_id),
            conversation_data=conversation_data
        )

        return conversation

    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_id: str = Depends(get_current_user_id_or_default),
    db: Session = Depends(get_db)
):
    """
    获取用户的对话列表

    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数
        user_id: 用户ID（从Token获取）
        db: 数据库会话

    Returns:
        对话列表
    """
    conversation_service = ConversationService(db)
    conversations = conversation_service.get_user_conversations(
        user_id=int(user_id),
        skip=skip,
        limit=limit
    )

    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
def get_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id_or_default),
    db: Session = Depends(get_db)
):
    """
    获取对话详情（包含消息）

    Args:
        conversation_id: 会话ID
        user_id: 用户ID（从Token获取）
        db: 数据库会话

    Returns:
        对话详情
    """
    try:
        conversation_service = ConversationService(db)
        conversation = conversation_service.get_conversation(
            conversation_id=conversation_id,
            user_id=int(user_id)
        )

        # 获取消息
        messages = conversation_service.get_messages(
            conversation_id=conversation_id,
            user_id=int(user_id)
        )

        # 构建响应
        return ConversationDetail(
            id=conversation.id,
            conversation_id=conversation.conversation_id,
            title=conversation.title,
            summary=conversation.summary,
            message_count=conversation.message_count,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[MessageResponse.from_orm(msg) for msg in messages]
        )

    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.put("/conversations/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: str,
    update_data: ConversationUpdate,
    user_id: str = Depends(get_current_user_id_or_default),
    db: Session = Depends(get_db)
):
    """
    更新对话

    Args:
        conversation_id: 会话ID
        update_data: 更新数据
        user_id: 用户ID（从Token获取）
        db: 数据库会话

    Returns:
        更新后的对话
    """
    try:
        conversation_service = ConversationService(db)
        conversation = conversation_service.update_conversation(
            conversation_id=conversation_id,
            user_id=int(user_id),
            update_data=update_data
        )

        return conversation

    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user_id_or_default),
    db: Session = Depends(get_db)
):
    """
    删除对话

    Args:
        conversation_id: 会话ID
        user_id: 用户ID（从Token获取）
        db: 数据库会话

    Returns:
        成功消息
    """
    try:
        conversation_service = ConversationService(db)
        conversation_service.delete_conversation(
            conversation_id=conversation_id,
            user_id=int(user_id)
        )

        return {"message": "对话删除成功"}

    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
def get_messages(
    conversation_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user_id: str = Depends(get_current_user_id_or_default),
    db: Session = Depends(get_db)
):
    """
    获取对话的消息列表

    Args:
        conversation_id: 会话ID
        skip: 跳过的记录数
        limit: 返回的最大记录数
        user_id: 用户ID（从Token获取）
        db: 数据库会话

    Returns:
        消息列表
    """
    try:
        conversation_service = ConversationService(db)
        messages = conversation_service.get_messages(
            conversation_id=conversation_id,
            user_id=int(user_id),
            skip=skip,
            limit=limit
        )

        return messages

    except ResourceNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AuthorizationError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )
