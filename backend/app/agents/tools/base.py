"""
工具系统抽象基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """工具参数定义"""
    type: str
    description: str
    enum: Optional[list] = None
    required: bool = True


class ToolSchema(BaseModel):
    """工具Schema定义"""
    name: str
    description: str
    parameters: Dict[str, ToolParameter]


class BaseTool(ABC):
    """工具抽象基类"""

    def __init__(self):
        self._name: Optional[str] = None
        self._description: Optional[str] = None

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass

    @property
    @abstractmethod
    def parameters_schema(self) -> Dict[str, Any]:
        """
        工具参数Schema

        返回OpenAI function calling格式的参数定义
        """
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """
        执行工具

        Args:
            **kwargs: 工具参数

        Returns:
            执行结果（字符串格式）

        Raises:
            ToolExecutionError: 工具执行失败
        """
        pass

    def get_openai_schema(self) -> Dict[str, Any]:
        """
        获取OpenAI格式的工具Schema

        Returns:
            OpenAI function calling格式的Schema
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema
            }
        }

    def validate_parameters(self, **kwargs) -> bool:
        """
        验证参数

        Args:
            **kwargs: 工具参数

        Returns:
            是否验证通过
        """
        required_params = self.parameters_schema.get("required", [])
        for param in required_params:
            if param not in kwargs:
                return False
        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name={self.name})>"
