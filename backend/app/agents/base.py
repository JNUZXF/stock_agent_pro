"""
智能体抽象基类
"""
from abc import ABC, abstractmethod
from typing import Generator, List, Dict, Any, Optional
import logging

from app.core.exceptions import AgentError

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """智能体抽象基类"""

    def __init__(
        self,
        user_id: str,
        conversation_id: Optional[str] = None,
        **kwargs
    ):
        """
        初始化智能体

        Args:
            user_id: 用户ID（用于用户隔离）
            conversation_id: 会话ID
            **kwargs: 其他参数
        """
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.conversation_history: List[Dict[str, Any]] = []

        logger.info(f"初始化智能体: user_id={user_id}, conversation_id={conversation_id}")

    @property
    @abstractmethod
    def agent_type(self) -> str:
        """智能体类型"""
        pass

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """系统提示词"""
        pass

    @abstractmethod
    def chat(self, user_message: str, **kwargs) -> Generator[str, None, None]:
        """
        聊天接口（流式输出）

        Args:
            user_message: 用户消息
            **kwargs: 其他参数

        Yields:
            响应内容片段

        Raises:
            AgentExecutionError: 智能体执行失败
        """
        pass

    def add_message(self, role: str, content: str, **kwargs) -> None:
        """
        添加消息到对话历史

        Args:
            role: 角色（user/assistant/system）
            content: 消息内容
            **kwargs: 其他字段
        """
        message = {"role": role, "content": content, **kwargs}
        self.conversation_history.append(message)
        logger.debug(f"添加消息: {role} - {len(content)} 字符")

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        return self.conversation_history.copy()

    def clear_history(self) -> None:
        """清空对话历史"""
        self.conversation_history.clear()
        logger.info(f"清空对话历史: conversation_id={self.conversation_id}")

    def get_context_messages(self, max_messages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取上下文消息

        Args:
            max_messages: 最大消息数（None表示全部）

        Returns:
            消息列表
        """
        if max_messages is None:
            return self.conversation_history

        # 保留系统消息 + 最近的N条消息
        system_messages = [msg for msg in self.conversation_history if msg.get("role") == "system"]
        other_messages = [msg for msg in self.conversation_history if msg.get("role") != "system"]

        if max_messages <= 0:
            return system_messages

        return system_messages + other_messages[-max_messages:]

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__}"
            f"(user_id={self.user_id}, conversation_id={self.conversation_id})>"
        )
