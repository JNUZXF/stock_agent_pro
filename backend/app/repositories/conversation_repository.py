"""
对话Repository
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.conversation import Conversation
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """对话Repository"""

    def __init__(self, db: Session):
        super().__init__(Conversation, db)

    def get_by_conversation_id(self, conversation_id: str) -> Optional[Conversation]:
        """
        根据会话ID获取对话

        Args:
            conversation_id: 会话ID

        Returns:
            对话对象或None
        """
        return (
            self.db.query(Conversation)
            .filter(Conversation.conversation_id == conversation_id)
            .first()
        )

    def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Conversation]:
        """
        获取用户的对话列表

        Args:
            user_id: 用户ID
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            对话列表
        """
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_user_id(self, user_id: int) -> int:
        """
        统计用户的对话数量

        Args:
            user_id: 用户ID

        Returns:
            对话数量
        """
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .count()
        )

    def exists_by_conversation_id(self, conversation_id: str) -> bool:
        """
        检查会话ID是否存在

        Args:
            conversation_id: 会话ID

        Returns:
            是否存在
        """
        return (
            self.db.query(Conversation)
            .filter(Conversation.conversation_id == conversation_id)
            .first() is not None
        )

    def increment_message_count(self, conversation_id: int) -> None:
        """
        增加消息计数

        Args:
            conversation_id: 对话数据库ID
        """
        conversation = self.get(conversation_id)
        if conversation:
            conversation.message_count += 1
            self.db.commit()

    def update_title_and_summary(
        self,
        conversation_id: int,
        title: Optional[str] = None,
        summary: Optional[str] = None
    ) -> Optional[Conversation]:
        """
        更新对话标题和摘要

        Args:
            conversation_id: 对话数据库ID
            title: 新标题
            summary: 新摘要

        Returns:
            更新后的对话对象
        """
        conversation = self.get(conversation_id)
        if conversation:
            if title is not None:
                conversation.title = title
            if summary is not None:
                conversation.summary = summary
            self.db.commit()
            self.db.refresh(conversation)
        return conversation
