"""
工具注册表
提供工具的注册、查找和管理功能
"""
from typing import Dict, List, Optional, Type
import logging

from app.agents.tools.base import BaseTool
from app.core.exceptions import ToolNotFoundError, ToolError

logger = logging.getLogger(__name__)


class ToolRegistry:
    """工具注册表（单例模式）"""

    _instance: Optional["ToolRegistry"] = None
    _tools: Dict[str, Type[BaseTool]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, tool_class: Type[BaseTool]) -> None:
        """
        注册工具类

        Args:
            tool_class: 工具类

        Raises:
            ToolError: 工具已存在
        """
        # 创建临时实例以获取名称
        temp_instance = tool_class()
        tool_name = temp_instance.name

        if tool_name in cls._tools:
            logger.warning(f"工具 {tool_name} 已存在，将被覆盖")

        cls._tools[tool_name] = tool_class
        logger.info(f"工具 {tool_name} 注册成功")

    @classmethod
    def unregister(cls, tool_name: str) -> None:
        """
        注销工具

        Args:
            tool_name: 工具名称
        """
        if tool_name in cls._tools:
            del cls._tools[tool_name]
            logger.info(f"工具 {tool_name} 注销成功")

    @classmethod
    def get_tool(cls, tool_name: str) -> BaseTool:
        """
        获取工具实例

        Args:
            tool_name: 工具名称

        Returns:
            工具实例

        Raises:
            ToolNotFoundError: 工具不存在
        """
        if tool_name not in cls._tools:
            raise ToolNotFoundError(
                f"工具 '{tool_name}' 未注册",
                details={"available_tools": list(cls._tools.keys())}
            )

        tool_class = cls._tools[tool_name]
        return tool_class()

    @classmethod
    def get_all_tools(cls) -> List[BaseTool]:
        """
        获取所有工具实例

        Returns:
            工具实例列表
        """
        return [tool_class() for tool_class in cls._tools.values()]

    @classmethod
    def get_tool_names(cls) -> List[str]:
        """
        获取所有工具名称

        Returns:
            工具名称列表
        """
        return list(cls._tools.keys())

    @classmethod
    def get_openai_schemas(cls) -> List[Dict]:
        """
        获取所有工具的OpenAI Schema

        Returns:
            OpenAI格式的工具Schema列表
        """
        tools = cls.get_all_tools()
        return [tool.get_openai_schema() for tool in tools]

    @classmethod
    def clear(cls) -> None:
        """清空所有注册的工具"""
        cls._tools.clear()
        logger.info("工具注册表已清空")

    @classmethod
    def count(cls) -> int:
        """
        获取注册的工具数量

        Returns:
            工具数量
        """
        return len(cls._tools)


def register_tool(tool_class: Type[BaseTool]) -> Type[BaseTool]:
    """
    工具注册装饰器

    Args:
        tool_class: 工具类

    Returns:
        原工具类

    Usage:
        @register_tool
        class MyTool(BaseTool):
            ...
    """
    ToolRegistry.register(tool_class)
    return tool_class


# 创建全局注册表实例
tool_registry = ToolRegistry()
