"""
对话服务
"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.core.exceptions import (
    ResourceNotFoundError,
    ResourceLimitExceededError,
    AuthorizationError
)
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    MessageCreate
)

logger = logging.getLogger(__name__)


class ConversationService:
    """对话服务"""

    def __init__(self, db: Session):
        self.db = db
        self.conversation_repo = ConversationRepository(db)
        self.message_repo = MessageRepository(db)

    def create_conversation(
        self,
        user_id: int,
        conversation_data: ConversationCreate
    ) -> Conversation:
        """
        创建对话

        Args:
            user_id: 用户ID
            conversation_data: 对话数据

        Returns:
            创建的对话对象

        Raises:
            ResourceAlreadyExistsError: 会话ID已存在
        """
        # 检查会话ID是否存在
        if self.conversation_repo.exists_by_conversation_id(conversation_data.conversation_id):
            raise ResourceNotFoundError(
                f"会话ID '{conversation_data.conversation_id}' 已存在"
            )

        # 创建对话
        conversation_dict = conversation_data.model_dump()
        conversation_dict["user_id"] = user_id

        conversation = self.conversation_repo.create(conversation_dict)

        logger.info(
            f"创建对话: user_id={user_id}, conversation_id={conversation.conversation_id}"
        )

        return conversation

    def get_conversation(
        self,
        conversation_id: str,
        user_id: int
    ) -> Conversation:
        """
        获取对话

        Args:
            conversation_id: 会话ID
            user_id: 用户ID

        Returns:
            对话对象

        Raises:
            ResourceNotFoundError: 对话不存在
            AuthorizationError: 无权访问
        """
        conversation = self.conversation_repo.get_by_conversation_id(conversation_id)

        if not conversation:
            raise ResourceNotFoundError(f"会话 '{conversation_id}' 不存在")

        # 检查权限
        if conversation.user_id != user_id:
            raise AuthorizationError("无权访问此会话")

        return conversation

    def get_user_conversations(
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
        return self.conversation_repo.get_by_user_id(user_id, skip, limit)

    def update_conversation(
        self,
        conversation_id: str,
        user_id: int,
        update_data: ConversationUpdate
    ) -> Conversation:
        """
        更新对话

        Args:
            conversation_id: 会话ID
            user_id: 用户ID
            update_data: 更新数据

        Returns:
            更新后的对话对象

        Raises:
            ResourceNotFoundError: 对话不存在
            AuthorizationError: 无权访问
        """
        conversation = self.get_conversation(conversation_id, user_id)

        # 更新
        update_dict = update_data.model_dump(exclude_unset=True)
        conversation = self.conversation_repo.update(conversation, update_dict)

        logger.info(f"更新对话: conversation_id={conversation_id}")

        return conversation

    def delete_conversation(
        self,
        conversation_id: str,
        user_id: int
    ) -> bool:
        """
        删除对话

        Args:
            conversation_id: 会话ID
            user_id: 用户ID

        Returns:
            是否删除成功

        Raises:
            ResourceNotFoundError: 对话不存在
            AuthorizationError: 无权访问
        """
        conversation = self.get_conversation(conversation_id, user_id)

        self.conversation_repo.delete(conversation.id)

        logger.info(f"删除对话: conversation_id={conversation_id}")

        return True

    def add_message(
        self,
        conversation_id: str,
        user_id: int,
        message_data: MessageCreate
    ) -> Message:
        """
        添加消息

        Args:
            conversation_id: 会话ID
            user_id: 用户ID
            message_data: 消息数据

        Returns:
            创建的消息对象

        Raises:
            ResourceNotFoundError: 对话不存在
            AuthorizationError: 无权访问
        """
        conversation = self.get_conversation(conversation_id, user_id)

        # 创建消息
        message_dict = message_data.model_dump()
        message_dict["conversation_id"] = conversation.id

        message = self.message_repo.create(message_dict)

        # 更新消息计数
        self.conversation_repo.increment_message_count(conversation.id)

        return message

    def get_messages(
        self,
        conversation_id: str,
        user_id: int,
        skip: int = 0,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        获取消息列表

        Args:
            conversation_id: 会话ID
            user_id: 用户ID
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            消息列表

        Raises:
            ResourceNotFoundError: 对话不存在
            AuthorizationError: 无权访问
        """
        conversation = self.get_conversation(conversation_id, user_id)

        return self.message_repo.get_by_conversation_id(
            conversation.id,
            skip,
            limit
        )

    def get_conversation_count(self, user_id: int) -> int:
        """
        获取用户的对话数量

        Args:
            user_id: 用户ID

        Returns:
            对话数量
        """
        return self.conversation_repo.count_by_user_id(user_id)
