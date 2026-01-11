"""
聊天服务
提供统一的聊天接口，协调智能体和数据库操作
"""
import logging
from typing import Generator, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.agents.manager import agent_manager
from app.services.conversation_service import ConversationService
from app.core.exceptions import AgentExecutionError
from app.schemas.conversation import ConversationCreate, MessageCreate
from app.schemas.chat import ChatChunkResponse

logger = logging.getLogger(__name__)


class ChatService:
    """聊天服务"""

    def __init__(self, db: Session):
        self.db = db
        self.conversation_service = ConversationService(db)

    def chat_stream(
        self,
        user_id: int,
        message: str,
        conversation_id: Optional[str] = None,
        agent_type: str = "stock_analysis"
    ) -> Generator[ChatChunkResponse, None, None]:
        """
        流式聊天

        Args:
            user_id: 用户ID
            message: 用户消息
            conversation_id: 会话ID（None则创建新会话）
            agent_type: 智能体类型

        Yields:
            聊天响应片段

        Raises:
            AgentExecutionError: 智能体执行失败
        """
        try:
            # 如果没有提供conversation_id，创建新会话
            if not conversation_id:
                conversation_id = self._generate_conversation_id()

                # 创建对话记录
                conversation_data = ConversationCreate(
                    conversation_id=conversation_id,
                    title=message[:50] if len(message) <= 50 else message[:47] + "..."
                )

                self.conversation_service.create_conversation(
                    user_id=user_id,
                    conversation_data=conversation_data
                )

                logger.info(f"创建新会话: {conversation_id}")

            else:
                # 验证会话是否存在且属于该用户
                self.conversation_service.get_conversation(conversation_id, user_id)

            # 保存用户消息到数据库
            user_message = MessageCreate(
                role="user",
                content=message
            )

            self.conversation_service.add_message(
                conversation_id=conversation_id,
                user_id=user_id,
                message_data=user_message
            )

            # 获取或创建智能体
            agent = agent_manager.get_agent(
                user_id=str(user_id),
                conversation_id=conversation_id,
                agent_type=agent_type
            )

            # 流式生成回复
            assistant_response = ""

            for chunk in agent.chat(message):
                assistant_response += chunk
                yield ChatChunkResponse(
                    type="chunk",
                    content=chunk,
                    conversation_id=conversation_id
                )

            # 保存助手回复到数据库
            assistant_message = MessageCreate(
                role="assistant",
                content=assistant_response
            )

            self.conversation_service.add_message(
                conversation_id=conversation_id,
                user_id=user_id,
                message_data=assistant_message
            )

            # 发送完成信号
            yield ChatChunkResponse(
                type="done",
                conversation_id=conversation_id
            )

            logger.info(f"聊天完成: conversation_id={conversation_id}")

        except Exception as e:
            logger.error(f"聊天失败: {str(e)}", exc_info=True)

            # 发送错误信息
            yield ChatChunkResponse(
                type="error",
                error=str(e),
                conversation_id=conversation_id
            )

    @staticmethod
    def _generate_conversation_id() -> str:
        """
        生成会话ID

        Returns:
            会话ID（格式: YYYYMMdd-HHmmss-XXXXX）
        """
        import random

        now = datetime.now()
        date_part = now.strftime("%Y%m%d-%H%M%S")
        random_part = f"{random.randint(10000, 99999)}"

        return f"{date_part}-{random_part}"
