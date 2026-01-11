"""
消息Repository
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import asc

from app.models.message import Message
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """消息Repository"""

    def __init__(self, db: Session):
        super().__init__(Message, db)

    def get_by_conversation_id(
        self,
        conversation_id: int,
        skip: int = 0,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        获取对话的消息列表

        Args:
            conversation_id: 对话数据库ID
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            消息列表
        """
        query = (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(asc(Message.created_at))
            .offset(skip)
        )

        if limit is not None:
            query = query.limit(limit)

        return query.all()

    def count_by_conversation_id(self, conversation_id: int) -> int:
        """
        统计对话的消息数量

        Args:
            conversation_id: 对话数据库ID

        Returns:
            消息数量
        """
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .count()
        )

    def delete_by_conversation_id(self, conversation_id: int) -> int:
        """
        删除对话的所有消息

        Args:
            conversation_id: 对话数据库ID

        Returns:
            删除的消息数量
        """
        count = (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .delete()
        )
        self.db.commit()
        return count

    def get_recent_messages(
        self,
        conversation_id: int,
        limit: int = 50
    ) -> List[Message]:
        """
        获取对话的最近消息

        Args:
            conversation_id: 对话数据库ID
            limit: 返回的最大记录数

        Returns:
            消息列表
        """
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(asc(Message.created_at))
            .limit(limit)
            .all()
        )
