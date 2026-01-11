"""
智能体管理器
提供智能体实例的创建、管理和清理功能
支持用户隔离
"""
import logging
from typing import Dict, Optional, Type
from datetime import datetime, timedelta

from app.agents.base import BaseAgent
from app.agents.stock_agent import StockAnalysisAgent
from app.config import settings
from app.core.exceptions import (
    AgentNotFoundError,
    ResourceLimitExceededError,
    AgentInitializationError
)

logger = logging.getLogger(__name__)


class AgentManager:
    """智能体管理器（单例模式）"""

    _instance: Optional["AgentManager"] = None

    # 智能体类型注册表
    AGENT_TYPES: Dict[str, Type[BaseAgent]] = {
        "stock_analysis": StockAnalysisAgent,
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._agents: Dict[str, Dict[str, BaseAgent]] = {}  # {user_id: {conversation_id: agent}}
            cls._instance._last_access: Dict[str, Dict[str, datetime]] = {}  # {user_id: {conversation_id: datetime}}
        return cls._instance

    def get_agent(
        self,
        user_id: str,
        conversation_id: str,
        agent_type: str = "stock_analysis",
        **kwargs
    ) -> BaseAgent:
        """
        获取或创建智能体实例

        Args:
            user_id: 用户ID
            conversation_id: 会话ID
            agent_type: 智能体类型
            **kwargs: 智能体初始化参数

        Returns:
            智能体实例

        Raises:
            AgentNotFoundError: 智能体类型不存在
            ResourceLimitExceededError: 超出资源限制
            AgentInitializationError: 智能体初始化失败
        """
        # 验证智能体类型
        if agent_type not in self.AGENT_TYPES:
            raise AgentNotFoundError(
                f"未知的智能体类型: {agent_type}",
                details={"available_types": list(self.AGENT_TYPES.keys())}
            )

        # 初始化用户的智能体字典
        if user_id not in self._agents:
            self._agents[user_id] = {}
            self._last_access[user_id] = {}

        # 检查用户的活跃智能体数量
        active_count = len(self._agents[user_id])
        if active_count >= settings.MAX_ACTIVE_AGENTS_PER_USER:
            # 尝试清理过期的智能体
            self._cleanup_user_agents(user_id)

            # 再次检查
            active_count = len(self._agents[user_id])
            if active_count >= settings.MAX_ACTIVE_AGENTS_PER_USER:
                raise ResourceLimitExceededError(
                    f"用户 {user_id} 的活跃智能体数量已达上限: {settings.MAX_ACTIVE_AGENTS_PER_USER}",
                    details={
                        "user_id": user_id,
                        "current_count": active_count,
                        "max_count": settings.MAX_ACTIVE_AGENTS_PER_USER
                    }
                )

        # 如果智能体已存在，更新访问时间并返回
        if conversation_id in self._agents[user_id]:
            logger.info(f"返回已存在的智能体: user_id={user_id}, conversation_id={conversation_id}")
            self._last_access[user_id][conversation_id] = datetime.now()
            return self._agents[user_id][conversation_id]

        # 创建新的智能体实例
        try:
            agent_class = self.AGENT_TYPES[agent_type]
            agent = agent_class(
                user_id=user_id,
                conversation_id=conversation_id,
                **kwargs
            )

            # 存储智能体和访问时间
            self._agents[user_id][conversation_id] = agent
            self._last_access[user_id][conversation_id] = datetime.now()

            logger.info(
                f"创建新智能体: user_id={user_id}, conversation_id={conversation_id}, type={agent_type}"
            )

            return agent

        except Exception as e:
            logger.error(f"智能体初始化失败: {str(e)}", exc_info=True)
            raise AgentInitializationError(
                f"智能体初始化失败: {str(e)}",
                details={"agent_type": agent_type, "user_id": user_id}
            )

    def remove_agent(self, user_id: str, conversation_id: str) -> bool:
        """
        移除智能体实例

        Args:
            user_id: 用户ID
            conversation_id: 会话ID

        Returns:
            是否移除成功
        """
        if user_id in self._agents and conversation_id in self._agents[user_id]:
            del self._agents[user_id][conversation_id]
            del self._last_access[user_id][conversation_id]

            # 如果用户没有智能体了，删除用户条目
            if not self._agents[user_id]:
                del self._agents[user_id]
                del self._last_access[user_id]

            logger.info(f"移除智能体: user_id={user_id}, conversation_id={conversation_id}")
            return True

        return False

    def _cleanup_user_agents(self, user_id: str) -> int:
        """
        清理用户的过期智能体

        Args:
            user_id: 用户ID

        Returns:
            清理的智能体数量
        """
        if user_id not in self._agents:
            return 0

        now = datetime.now()
        timeout = timedelta(minutes=settings.CONVERSATION_TIMEOUT_MINUTES)
        expired_conversations = []

        # 查找过期的会话
        for conversation_id, last_access in self._last_access[user_id].items():
            if now - last_access > timeout:
                expired_conversations.append(conversation_id)

        # 移除过期的智能体
        for conversation_id in expired_conversations:
            self.remove_agent(user_id, conversation_id)

        if expired_conversations:
            logger.info(
                f"清理过期智能体: user_id={user_id}, count={len(expired_conversations)}"
            )

        return len(expired_conversations)

    def cleanup_all_expired(self) -> int:
        """
        清理所有过期的智能体

        Returns:
            清理的智能体总数
        """
        total_cleaned = 0
        user_ids = list(self._agents.keys())

        for user_id in user_ids:
            total_cleaned += self._cleanup_user_agents(user_id)

        if total_cleaned > 0:
            logger.info(f"清理所有过期智能体: total={total_cleaned}")

        return total_cleaned

    def get_user_agent_count(self, user_id: str) -> int:
        """
        获取用户的活跃智能体数量

        Args:
            user_id: 用户ID

        Returns:
            智能体数量
        """
        return len(self._agents.get(user_id, {}))

    def get_total_agent_count(self) -> int:
        """
        获取所有活跃智能体总数

        Returns:
            智能体总数
        """
        return sum(len(agents) for agents in self._agents.values())

    def clear_user_agents(self, user_id: str) -> int:
        """
        清空用户的所有智能体

        Args:
            user_id: 用户ID

        Returns:
            清理的智能体数量
        """
        count = self.get_user_agent_count(user_id)

        if user_id in self._agents:
            del self._agents[user_id]
            del self._last_access[user_id]
            logger.info(f"清空用户智能体: user_id={user_id}, count={count}")

        return count

    def clear_all(self) -> None:
        """清空所有智能体"""
        total = self.get_total_agent_count()
        self._agents.clear()
        self._last_access.clear()
        logger.info(f"清空所有智能体: total={total}")


# 创建全局管理器实例
agent_manager = AgentManager()
