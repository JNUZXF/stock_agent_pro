"""
股票分析智能体
"""
import json
import logging
import asyncio
from typing import Generator, Optional, List, Dict, Any, AsyncGenerator
from openai import AsyncOpenAI

from app.agents.base import BaseAgent
from app.agents.tools.registry import tool_registry
from app.config import settings
from app.core.exceptions import AgentExecutionError, AIServiceError, ToolExecutionError

logger = logging.getLogger(__name__)


class StockAnalysisAgent(BaseAgent):
    """股票分析智能体"""

    def __init__(
        self,
        user_id: str,
        conversation_id: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        初始化股票分析智能体

        Args:
            user_id: 用户ID
            conversation_id: 会话ID
            api_key: AI服务API密钥
            base_url: AI服务基础URL
            model: 模型名称
        """
        super().__init__(user_id, conversation_id)

        # AI服务配置（支持多种环境变量名称）
        self.api_key = api_key or settings.effective_ai_api_key
        self.base_url = base_url or settings.AI_BASE_URL
        self.model = model or settings.AI_MODEL
        
        # 验证API密钥是否存在
        if not self.api_key:
            raise ValueError(
                "API密钥未设置。请设置以下环境变量之一：\n"
                "- AI_API_KEY (推荐)\n"
                "- DOUBAO_API_KEY (备选)\n"
                "或者在初始化时直接传递 api_key 参数"
            )

        # 创建异步OpenAI客户端
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        # 初始化系统提示词
        self.add_message("system", self.system_prompt)

        logger.info(f"股票分析智能体初始化完成: user_id={user_id}, model={self.model}")

    @property
    def agent_type(self) -> str:
        return "stock_analysis"

    @property
    def system_prompt(self) -> str:
        return """你是一个专业的股票分析助手。你可以：
1. 查询股票的详细财务信息
2. 分析股票的投资价值
3. 提供专业的投资建议

请用专业、客观的态度回答用户的问题，并在需要时主动调用工具获取最新的股票数据。"""

    def chat(
        self,
        user_message: str,
        max_iterations: int = 5,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        聊天接口（同步流式输出，内部调用异步实现）

        Args:
            user_message: 用户消息
            max_iterations: 最大迭代次数（防止无限循环）
            **kwargs: 其他参数

        Yields:
            响应内容片段

        Raises:
            AgentExecutionError: 智能体执行失败
        """
        # 获取或创建事件循环
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # 使用异步生成器
        async_gen = self.chat_async(user_message, max_iterations, **kwargs)
        
        # 将异步生成器转换为同步生成器
        while True:
            try:
                chunk = loop.run_until_complete(async_gen.__anext__())
                yield chunk
            except StopAsyncIteration:
                break
    
    async def chat_async(
        self,
        user_message: str,
        max_iterations: int = 5,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        异步聊天接口（流式输出）

        Args:
            user_message: 用户消息
            max_iterations: 最大迭代次数（防止无限循环）
            **kwargs: 其他参数

        Yields:
            响应内容片段

        Raises:
            AgentExecutionError: 智能体执行失败
        """
        try:
            # 添加用户消息
            self.add_message("user", user_message)

            # 获取所有可用工具的Schema
            tools = tool_registry.get_openai_schemas()

            iteration = 0
            while iteration < max_iterations:
                iteration += 1
                logger.debug(f"开始第 {iteration} 次迭代")

                # 调用AI模型（异步）
                try:
                    response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=self.get_context_messages(
                            max_messages=settings.MAX_CONVERSATION_HISTORY
                        ),
                        tools=tools if tools else None,
                        stream=True,
                        temperature=settings.AI_TEMPERATURE,
                        max_tokens=settings.AI_MAX_TOKENS
                    )
                except Exception as e:
                    logger.error(f"AI服务调用失败: {str(e)}")
                    raise AIServiceError(f"AI服务调用失败: {str(e)}")

                # 处理流式响应
                full_content = ""
                tool_calls_data = []
                current_tool_call = None

                async for chunk in response:
                    delta = chunk.choices[0].delta

                    # 处理内容
                    if delta.content:
                        full_content += delta.content
                        yield delta.content

                    # 处理工具调用
                    if delta.tool_calls:
                        for tool_call_delta in delta.tool_calls:
                            if tool_call_delta.index is not None:
                                # 新的工具调用
                                if current_tool_call is None or tool_call_delta.index != current_tool_call.get("index"):
                                    if current_tool_call:
                                        tool_calls_data.append(current_tool_call)
                                    current_tool_call = {
                                        "index": tool_call_delta.index,
                                        "id": tool_call_delta.id or "",
                                        "type": "function",
                                        "function": {
                                            "name": tool_call_delta.function.name or "",
                                            "arguments": tool_call_delta.function.arguments or ""
                                        }
                                    }
                                else:
                                    # 继续累积工具调用数据
                                    if tool_call_delta.function.name:
                                        current_tool_call["function"]["name"] += tool_call_delta.function.name
                                    if tool_call_delta.function.arguments:
                                        current_tool_call["function"]["arguments"] += tool_call_delta.function.arguments

                # 添加最后一个工具调用
                if current_tool_call:
                    tool_calls_data.append(current_tool_call)

                finish_reason = chunk.choices[0].finish_reason

                # 如果需要调用工具
                if finish_reason == "tool_calls" and tool_calls_data:
                    logger.info(f"需要调用 {len(tool_calls_data)} 个工具")

                    # 添加助手的工具调用消息
                    tool_calls_for_message = [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["function"]["name"],
                                "arguments": tc["function"]["arguments"]
                            }
                        }
                        for tc in tool_calls_data
                    ]

                    self.add_message(
                        "assistant",
                        content=full_content if full_content else "",
                        tool_calls=tool_calls_for_message
                    )

                    # 并发执行所有工具调用（性能优化）
                    tool_tasks = []
                    for tool_call in tool_calls_data:
                        tool_name = tool_call["function"]["name"]
                        tool_arguments = tool_call["function"]["arguments"]
                        tool_call_id = tool_call["id"]
                        
                        task = self._execute_tool_async(
                            tool_name, 
                            tool_arguments, 
                            tool_call_id
                        )
                        tool_tasks.append(task)
                    
                    # 等待所有工具执行完成
                    await asyncio.gather(*tool_tasks, return_exceptions=True)

                    # 继续下一轮迭代
                    continue

                # 如果完成了回复
                elif finish_reason == "stop":
                    if full_content:
                        self.add_message("assistant", full_content)
                    logger.info("对话完成")
                    break

                else:
                    # 其他情况
                    if full_content:
                        self.add_message("assistant", full_content)
                    logger.warning(f"未知的结束原因: {finish_reason}")
                    break

            if iteration >= max_iterations:
                logger.warning(f"达到最大迭代次数: {max_iterations}")

        except AIServiceError:
            raise
        except Exception as e:
            logger.error(f"智能体执行失败: {str(e)}", exc_info=True)
            raise AgentExecutionError(f"智能体执行失败: {str(e)}")

    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        执行工具（同步）

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果

        Raises:
            ToolExecutionError: 工具执行失败
        """
        try:
            tool = tool_registry.get_tool(tool_name)
            result = tool.execute(**arguments)
            return result
        except Exception as e:
            logger.error(f"工具 {tool_name} 执行失败: {str(e)}")
            raise ToolExecutionError(
                f"工具执行失败: {str(e)}",
                details={"tool_name": tool_name, "arguments": arguments}
            )
    
    async def _execute_tool_async(
        self, 
        tool_name: str, 
        tool_arguments: str, 
        tool_call_id: str
    ) -> None:
        """
        异步执行工具并添加结果到消息历史

        Args:
            tool_name: 工具名称
            tool_arguments: 工具参数（JSON字符串）
            tool_call_id: 工具调用ID
        """
        try:
            # 解析参数
            arguments = json.loads(tool_arguments)

            # 执行工具
            logger.info(f"执行工具: {tool_name}, 参数: {arguments}")
            
            # 检查工具是否支持异步执行
            tool = tool_registry.get_tool(tool_name)
            if hasattr(tool, 'execute_async'):
                # 使用异步方法
                tool_result = await tool.execute_async(**arguments)
            else:
                # 在线程池中执行同步方法
                loop = asyncio.get_event_loop()
                tool_result = await loop.run_in_executor(
                    None, 
                    lambda: tool.execute(**arguments)
                )

            # 添加工具结果消息
            self.add_message(
                "tool",
                content=tool_result,
                tool_call_id=tool_call_id
            )

            logger.info(f"工具 {tool_name} 执行成功")

        except json.JSONDecodeError as e:
            error_msg = f"工具参数解析失败: {str(e)}"
            logger.error(error_msg)
            self.add_message(
                "tool",
                content=error_msg,
                tool_call_id=tool_call_id
            )

        except ToolExecutionError as e:
            error_msg = f"工具执行失败: {str(e)}"
            logger.error(error_msg)
            self.add_message(
                "tool",
                content=error_msg,
                tool_call_id=tool_call_id
            )
        except Exception as e:
            error_msg = f"工具执行异常: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.add_message(
                "tool",
                content=error_msg,
                tool_call_id=tool_call_id
            )