"""
股票数据工具
"""
import logging
import json
import sys
import os
import asyncio
import time
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor
import pysnowball as ball

from app.agents.tools.base import BaseTool
from app.agents.tools.registry import register_tool
from app.core.exceptions import ToolExecutionError

logger = logging.getLogger(__name__)

# 创建线程池用于执行同步的pysnowball API调用
_executor = ThreadPoolExecutor(max_workers=10)

# 设置默认编码为UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 确保使用UTF-8编码
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    import io
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


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
        执行股票信息查询（同步接口，内部调用异步实现）

        Args:
            symbol: 股票代码

        Returns:
            股票详细信息的字符串表示
        """
        # 获取或创建事件循环
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # 运行异步方法
        return loop.run_until_complete(self.execute_async(**kwargs))
    
    async def execute_async(self, **kwargs) -> str:
        """
        异步执行股票信息查询

        Args:
            symbol: 股票代码

        Returns:
            股票详细信息的字符串表示
        """
        tool_start_time = time.time()
        symbol = kwargs.get("symbol")

        if not symbol:
            raise ToolExecutionError(
                "缺少必需参数: symbol",
                details=kwargs
            )

        try:
            logger.info(f"查询股票信息: {symbol}")

            # 设置token（从环境变量读取，如果没有则使用默认值）
            # 确保token字符串使用UTF-8编码
            import os
            from dotenv import load_dotenv
            perf_token_start = time.time()
            load_dotenv()
            
            xq_token = os.getenv("xq_a_token", "")
            if xq_token:
                token = f'xq_a_token={xq_token};'
            else:
                # 如果没有设置token，使用默认值（但实际应该要求用户设置）
                token = 'xq_a_token=填入你的token;'
            
            # 确保token是UTF-8编码的字符串
            if isinstance(token, bytes):
                token = token.decode('utf-8', errors='ignore')
            elif isinstance(token, str):
                # 确保字符串是有效的UTF-8
                token = token.encode('utf-8', errors='ignore').decode('utf-8')
            
            ball.set_token(token)
            perf_token_end = time.time()
            logger.info(f"[PERF] Token设置耗时: {(perf_token_end - perf_token_start) * 1000:.2f}ms")

            # 并发获取股票基本信息，使用UTF-8编码处理返回结果
            # 使用asyncio.gather并发执行多个API调用，大幅提升速度
            perf_api_start = time.time()
            cash_flow_task = self._safe_get_data_async(lambda: ball.cash_flow(symbol))
            income_task = self._safe_get_data_async(lambda: ball.income(symbol))
            business_task = self._safe_get_data_async(lambda: ball.business(symbol))
            holders_task = self._safe_get_data_async(lambda: ball.top_holders(symbol))
            
            # 并发执行所有API调用
            cash_flow, income_statement, business_analysis, holders = await asyncio.gather(
                cash_flow_task,
                income_task,
                business_task,
                holders_task,
                return_exceptions=True
            )
            perf_api_end = time.time()
            logger.info(f"[PERF] 股票API并发调用总耗时: {(perf_api_end - perf_api_start) * 1000:.2f}ms")
            
            # 处理可能的异常
            for i, result in enumerate([cash_flow, income_statement, business_analysis, holders]):
                if isinstance(result, Exception):
                    logger.warning(f"API调用 {i} 失败: {result}")

            # 格式化返回结果，确保使用UTF-8编码
            result = f"""
股票代码: {symbol}

【现金流分析】
{self._format_dict(cash_flow if not isinstance(cash_flow, Exception) else None)}

【收入分析】
{self._format_dict(income_statement if not isinstance(income_statement, Exception) else None)}

【主营业务分析】
{self._format_dict(business_analysis if not isinstance(business_analysis, Exception) else None)}

【主要股东】
{self._format_dict(holders if not isinstance(holders, Exception) else None)}
"""
            logger.info(f"股票信息查询成功: {symbol}")
            # 确保返回的字符串是UTF-8编码
            return result.strip().encode('utf-8').decode('utf-8')

        except Exception as e:
            error_msg = str(e)
            logger.error(f"股票信息查询失败: {symbol}, 错误: {error_msg}")
            raise ToolExecutionError(
                f"查询股票信息失败: {error_msg}",
                details={"symbol": symbol}
            )
    
    @staticmethod
    async def _safe_get_data_async(func):
        """
        异步安全获取数据，处理编码问题
        
        Args:
            func: 调用pysnowball API的函数
            
        Returns:
            处理后的数据
        """
        loop = asyncio.get_event_loop()
        
        try:
            # 在线程池中执行同步API调用
            data = await loop.run_in_executor(_executor, func)
            
            # 如果数据为空，直接返回
            if data is None:
                return None
            
            # 将数据转换为JSON字符串再解析，确保编码正确
            # 这样可以处理所有编码问题，包括latin-1编码错误
            try:
                json_str = json.dumps(data, ensure_ascii=False, default=str)
                return json.loads(json_str)
            except (UnicodeEncodeError, UnicodeDecodeError, TypeError) as e:
                logger.warning(f"JSON序列化/反序列化时出现编码问题: {str(e)}，尝试修复")
                # 如果JSON处理失败，尝试递归处理数据
                return StockInfoTool._fix_encoding(data)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            logger.warning(f"编码错误，尝试修复: {str(e)}")
            # 如果出现编码错误，尝试使用JSON序列化/反序列化来修复
            try:
                data = await loop.run_in_executor(_executor, func)
                if data is None:
                    return None
                json_str = json.dumps(data, ensure_ascii=False, default=str)
                return json.loads(json_str)
            except Exception as e2:
                logger.error(f"修复编码错误失败: {str(e2)}")
                raise ToolExecutionError(f"数据编码处理失败: {str(e2)}")
        except Exception as e:
            # 其他异常直接抛出
            logger.error(f"获取数据失败: {str(e)}")
            raise
    
    @staticmethod
    def _safe_get_data(func):
        """
        同步安全获取数据，处理编码问题（保留用于向后兼容）
        
        Args:
            func: 调用pysnowball API的函数
            
        Returns:
            处理后的数据
        """
        try:
            data = func()
            # 如果数据为空，直接返回
            if data is None:
                return None
            
            # 将数据转换为JSON字符串再解析，确保编码正确
            # 这样可以处理所有编码问题，包括latin-1编码错误
            try:
                json_str = json.dumps(data, ensure_ascii=False, default=str)
                return json.loads(json_str)
            except (UnicodeEncodeError, UnicodeDecodeError, TypeError) as e:
                logger.warning(f"JSON序列化/反序列化时出现编码问题: {str(e)}，尝试修复")
                # 如果JSON处理失败，尝试递归处理数据
                return StockInfoTool._fix_encoding(data)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            logger.warning(f"编码错误，尝试修复: {str(e)}")
            # 如果出现编码错误，尝试使用JSON序列化/反序列化来修复
            try:
                data = func()
                if data is None:
                    return None
                json_str = json.dumps(data, ensure_ascii=False, default=str)
                return json.loads(json_str)
            except Exception as e2:
                logger.error(f"修复编码错误失败: {str(e2)}")
                raise ToolExecutionError(f"数据编码处理失败: {str(e2)}")
        except Exception as e:
            # 其他异常直接抛出
            logger.error(f"获取数据失败: {str(e)}")
            raise
    
    @staticmethod
    def _fix_encoding(obj):
        """
        递归修复对象中的编码问题
        
        Args:
            obj: 要修复的对象
            
        Returns:
            修复后的对象
        """
        if obj is None:
            return None
        elif isinstance(obj, str):
            # 如果是字符串，确保是UTF-8编码
            try:
                return obj.encode('utf-8', errors='ignore').decode('utf-8')
            except Exception:
                return str(obj)
        elif isinstance(obj, bytes):
            # 如果是字节串，尝试解码为UTF-8
            try:
                return obj.decode('utf-8', errors='ignore')
            except Exception:
                return obj.decode('latin-1', errors='ignore')
        elif isinstance(obj, dict):
            # 如果是字典，递归处理每个值
            return {k: StockInfoTool._fix_encoding(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            # 如果是列表，递归处理每个元素
            return [StockInfoTool._fix_encoding(item) for item in obj]
        else:
            # 其他类型，尝试转换为字符串
            try:
                return str(obj).encode('utf-8', errors='ignore').decode('utf-8')
            except Exception:
                return obj

    @staticmethod
    def _format_dict(data: Any, indent: int = 0) -> str:
        """
        格式化字典为可读字符串，确保正确处理中文字符
        
        Args:
            data: 要格式化的数据（可以是dict、list或其他类型）
            indent: 缩进级别
            
        Returns:
            格式化后的字符串
        """
        if data is None:
            return "无数据"
        
        if not isinstance(data, dict):
            # 如果不是字典，尝试转换为字符串，确保UTF-8编码
            try:
                result = str(data)
                return result.encode('utf-8', errors='ignore').decode('utf-8')
            except Exception:
                return json.dumps(data, ensure_ascii=False, default=str)

        lines = []
        for key, value in data.items():
            prefix = "  " * indent
            # 确保key是字符串且使用UTF-8编码
            key_str = str(key).encode('utf-8', errors='ignore').decode('utf-8')
            
            if isinstance(value, dict):
                lines.append(f"{prefix}{key_str}:")
                lines.append(StockInfoTool._format_dict(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key_str}: {len(value)} 项")
                # 如果列表较短，可以显示部分内容
                if len(value) > 0 and len(value) <= 3:
                    for i, item in enumerate(value):
                        lines.append(f"{prefix}  [{i+1}] {StockInfoTool._format_dict(item if isinstance(item, dict) else {'value': item}, indent + 1)}")
            else:
                # 确保value是字符串且使用UTF-8编码
                try:
                    value_str = str(value).encode('utf-8', errors='ignore').decode('utf-8')
                    lines.append(f"{prefix}{key_str}: {value_str}")
                except Exception:
                    # 如果转换失败，使用JSON序列化
                    value_str = json.dumps(value, ensure_ascii=False, default=str)
                    lines.append(f"{prefix}{key_str}: {value_str}")

        result = "\n".join(lines)
        # 确保返回的字符串使用UTF-8编码
        return result.encode('utf-8', errors='ignore').decode('utf-8')
