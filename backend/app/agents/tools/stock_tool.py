"""
股票数据工具
"""
import logging
from typing import Dict, Any
import pysnowball as ball

from app.agents.tools.base import BaseTool
from app.agents.tools.registry import register_tool
from app.core.exceptions import ToolExecutionError

logger = logging.getLogger(__name__)


@register_tool
class StockInfoTool(BaseTool):
    """股票信息查询工具"""

    @property
    def name(self) -> str:
        return "get_stock_info"

    @property
    def description(self) -> str:
        return "获取股票的详细财务信息，包括现金流、收入、主营业务和股东信息等"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "股票代码，例如：SH600519（贵州茅台）"
                }
            },
            "required": ["symbol"]
        }

    def execute(self, **kwargs) -> str:
        """
        执行股票信息查询

        Args:
            symbol: 股票代码

        Returns:
            股票详细信息的字符串表示
        """
        symbol = kwargs.get("symbol")

        if not symbol:
            raise ToolExecutionError(
                "缺少必需参数: symbol",
                details=kwargs
            )

        try:
            logger.info(f"查询股票信息: {symbol}")

            # 设置token（使用雪球网站的默认值）
            ball.set_token('xq_a_token=填入你的token;')

            # 获取股票基本信息
            cash_flow = ball.cash_flow(symbol)
            income_statement = ball.income(symbol)
            business_analysis = ball.business(symbol)
            holders = ball.top_holders(symbol)

            # 格式化返回结果
            result = f"""
股票代码: {symbol}

【现金流分析】
{self._format_dict(cash_flow)}

【收入分析】
{self._format_dict(income_statement)}

【主营业务分析】
{self._format_dict(business_analysis)}

【主要股东】
{self._format_dict(holders)}
"""
            logger.info(f"股票信息查询成功: {symbol}")
            return result.strip()

        except Exception as e:
            logger.error(f"股票信息查询失败: {symbol}, 错误: {str(e)}")
            raise ToolExecutionError(
                f"查询股票信息失败: {str(e)}",
                details={"symbol": symbol}
            )

    @staticmethod
    def _format_dict(data: Dict, indent: int = 0) -> str:
        """格式化字典为可读字符串"""
        if not isinstance(data, dict):
            return str(data)

        lines = []
        for key, value in data.items():
            prefix = "  " * indent
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(StockInfoTool._format_dict(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}: {len(value)} 项")
            else:
                lines.append(f"{prefix}{key}: {value}")

        return "\n".join(lines)
