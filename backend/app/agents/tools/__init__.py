"""
工具包
"""
from app.agents.tools.base import BaseTool, ToolSchema, ToolParameter
from app.agents.tools.registry import ToolRegistry, tool_registry, register_tool
from app.agents.tools.stock_tool import StockInfoTool

# 自动导入时注册所有工具
# 工具会通过@register_tool装饰器自动注册

__all__ = [
    "BaseTool",
    "ToolSchema",
    "ToolParameter",
    "ToolRegistry",
    "tool_registry",
    "register_tool",
    "StockInfoTool",
]
