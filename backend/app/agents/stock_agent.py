"""
股票分析智能体
"""
import json
import logging
import asyncio
import time
from typing import Generator, Optional, List, Dict, Any, AsyncGenerator
from openai import AsyncOpenAI, OpenAI
from concurrent.futures import ThreadPoolExecutor

from app.agents.base import BaseAgent
from app.agents.tools.registry import tool_registry
from app.config import settings
from app.core.exceptions import AgentExecutionError, AIServiceError, ToolExecutionError

logger = logging.getLogger(__name__)

# 创建线程池用于执行同步的responses API调用
_responses_executor = ThreadPoolExecutor(max_workers=10)


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

        # 创建异步OpenAI客户端（用于chat.completions API）
        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # 创建同步OpenAI客户端（用于responses API，性能更好）
        self.sync_client = OpenAI(
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
        # 性能计时开始
        perf_timestamps = {}
        perf_timestamps['agent_start'] = time.time()
        
        try:
            # 添加用户消息
            self.add_message("user", user_message)
            perf_timestamps['message_added'] = time.time()
            logger.info(f"[PERF] 添加用户消息耗时: {(perf_timestamps['message_added'] - perf_timestamps['agent_start']) * 1000:.2f}ms")

            # 获取所有可用工具的Schema
            tools = tool_registry.get_openai_schemas()
            perf_timestamps['tools_schema_obtained'] = time.time()
            logger.info(f"[PERF] 获取工具Schema耗时: {(perf_timestamps['tools_schema_obtained'] - perf_timestamps['message_added']) * 1000:.2f}ms")

            iteration = 0
            while iteration < max_iterations:
                iteration += 1
                logger.debug(f"开始第 {iteration} 次迭代")
                perf_timestamps[f'iteration_{iteration}_start'] = time.time()

                # 准备conversations格式（responses API使用）
                conversations = self._prepare_responses_conversations(
                    max_messages=settings.MAX_CONVERSATION_HISTORY
                )

                # 调用AI模型（使用responses API，性能更好）
                try:
                    perf_timestamps[f'ai_request_start'] = time.time()
                    
                    # 在线程池中执行同步的responses API调用
                    # 注意：responses API的工具格式可能不同，暂时不传递tools参数
                    # 如果需要工具调用，可以使用chat.completions API
                    loop = asyncio.get_event_loop()
                    
                    # 简单对话使用responses API（性能更好）
                    # 注意：responses API目前不支持tools参数，需要工具时使用chat.completions API
                    # 这里先测试简单对话的性能
                    response = await loop.run_in_executor(
                        _responses_executor,
                        lambda: self.sync_client.responses.create(
                            model=self.model,
                            input=conversations,
                            stream=True,
                            extra_body={"thinking": {"type": "disabled"}}
                        )
                    )
                    use_chat_api = False
                    perf_timestamps[f'ai_response_received'] = time.time()
                    ai_request_time = (perf_timestamps[f'ai_response_received'] - perf_timestamps[f'ai_request_start']) * 1000
                    logger.info(f"[PERF] AI请求耗时（到收到流）: {ai_request_time:.2f}ms")
                except Exception as e:
                    logger.error(f"AI服务调用失败: {str(e)}")
                    raise AIServiceError(f"AI服务调用失败: {str(e)}")

                # 处理responses API的流式响应
                full_content = ""
                first_content_time = None
                response_type = None
                tool_call = False
                latest_event = None

                # 将同步生成器转换为异步生成器
                for i, event in enumerate(response):
                    latest_event = event
                    
                    # 检查响应类型（responses API在第2个事件时确定类型）
                    if i == 2:
                        import openai
                        if type(event) == openai.types.responses.response_output_item_added_event.ResponseOutputItemAddedEvent:
                            if event.item.type == "function_call":
                                response_type = "function_call"
                                tool_call = True
                            else:
                                response_type = "stream"
                    
                    # 处理内容流
                    if hasattr(event, "delta") and response_type == "stream":
                        if first_content_time is None:
                            first_content_time = time.time()
                            time_to_first_content = (first_content_time - perf_timestamps[f'ai_request_start']) * 1000
                            logger.info(f"[PERF] ⚡ 首Token到达Agent层耗时: {time_to_first_content:.2f}ms")
                        full_content += event.delta
                        yield event.delta

                # 处理responses API的工具调用
                # responses API在response.output中返回工具调用信息
                if tool_call and latest_event and hasattr(latest_event, 'response'):
                    try:
                        import openai
                        if hasattr(latest_event.response, 'output') and len(latest_event.response.output) > 0:
                            output_item = latest_event.response.output[0]
                            if hasattr(output_item, 'type') and output_item.type == "function_call":
                                call_id = output_item.call_id
                                tool_name = output_item.name
                                arguments = output_item.arguments
                                
                                # 解析工具调用参数
                                call_arguments = json.loads(arguments)
                                
                                # 执行工具
                                perf_timestamps['tool_call_start'] = time.time()
                                logger.info(f"需要调用工具: {tool_name}")
                                
                                # 执行工具并获取结果
                                tool_result = await self._execute_tool_async_simple(tool_name, call_arguments)
                                
                                # 添加工具调用结果到conversation_history（responses API格式）
                                self.conversation_history.append({
                                    "type": "function_call_output",
                                    "call_id": call_id,
                                    "output": json.dumps(tool_result, ensure_ascii=False)
                                })
                                
                                perf_timestamps['tool_execution_end'] = time.time()
                                tool_execution_time = (perf_timestamps['tool_execution_end'] - perf_timestamps['tool_call_start']) * 1000
                                logger.info(f"[PERF] 工具执行总耗时: {tool_execution_time:.2f}ms")
                                
                                # 使用previous_response_id继续对话（responses API的方式）
                                # 这里需要重新准备conversations并继续下一轮
                                # 注意：responses API使用previous_response_id而不是重新发送所有消息
                                conversations = self._prepare_responses_conversations(
                                    max_messages=settings.MAX_CONVERSATION_HISTORY
                                )
                                
                                # 继续下一轮迭代，使用previous_response_id
                                response = await loop.run_in_executor(
                                    _responses_executor,
                                    lambda: self.sync_client.responses.create(
                                        model=self.model,
                                        previous_response_id=latest_event.response.id,
                                        input=conversations,
                                        stream=True,
                                        tools=tools if tools else None,
                                        extra_body={"thinking": {"type": "disabled"}}
                                    )
                                )
                                
                                # 重置状态，继续处理新的响应流
                                full_content = ""
                                response_type = None
                                tool_call = False
                                latest_event = None
                                first_content_time = None
                                
                                # 继续处理新的响应流（会在外层循环继续）
                                continue
                    except Exception as e:
                        logger.error(f"处理工具调用失败: {str(e)}", exc_info=True)
                        raise

                # 如果完成了回复（没有工具调用）
                if response_type == "stream" and not tool_call:
                    if full_content:
                        self.add_message("assistant", full_content)
                    logger.info("对话完成")
                    break
                elif tool_call:
                    # 工具调用已处理，继续下一轮迭代（在工具调用处理中已continue）
                    pass
                else:
                    # 其他情况
                    if full_content:
                        self.add_message("assistant", full_content)
                    logger.warning(f"未知的响应类型: {response_type}")
                    break

            if iteration >= max_iterations:
                logger.warning(f"达到最大迭代次数: {max_iterations}")

        except AIServiceError:
            raise
        except Exception as e:
            logger.error(f"智能体执行失败: {str(e)}", exc_info=True)
            raise AgentExecutionError(f"智能体执行失败: {str(e)}")

    def _prepare_responses_conversations(self, max_messages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        准备responses API格式的conversations
        
        Args:
            max_messages: 最大消息数
            
        Returns:
            responses API格式的conversations列表
        """
        messages = self.get_context_messages(max_messages)
        conversations = []
        
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            
            if role == "system":
                conversations.append({
                    "type": "message",
                    "role": "system",
                    "content": content
                })
            elif role == "user":
                conversations.append({
                    "type": "message",
                    "role": "user",
                    "content": content
                })
            elif role == "assistant":
                # 处理工具调用
                if "tool_calls" in msg:
                    conversations.append({
                        "type": "message",
                        "role": "assistant",
                        "content": content,
                        "tool_calls": msg["tool_calls"]
                    })
                else:
                    conversations.append({
                        "type": "message",
                        "role": "assistant",
                        "content": content
                    })
            elif role == "tool" or "call_id" in msg:
                # 工具调用结果
                conversations.append({
                    "type": "function_call_output",
                    "call_id": msg.get("tool_call_id") or msg.get("call_id"),
                    "output": msg.get("content", "")
                })
        
        return conversations
    
    async def _execute_tool_async_simple(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        简单异步工具执行（用于responses API）
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        try:
            tool = tool_registry.get_tool(tool_name)
            if hasattr(tool, 'execute_async'):
                return await tool.execute_async(**arguments)
            else:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(
                    None,
                    lambda: tool.execute(**arguments)
                )
        except Exception as e:
            logger.error(f"工具 {tool_name} 执行失败: {str(e)}")
            raise ToolExecutionError(f"工具执行失败: {str(e)}")

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
        tool_perf_start = time.time()
        try:
            # 解析参数
            arguments = json.loads(tool_arguments)
            perf_parse = time.time()
            logger.info(f"[PERF] 工具参数解析耗时: {(perf_parse - tool_perf_start) * 1000:.2f}ms")

            # 执行工具
            logger.info(f"执行工具: {tool_name}, 参数: {arguments}")
            
            # 检查工具是否支持异步执行
            tool = tool_registry.get_tool(tool_name)
            perf_tool_get = time.time()
            logger.info(f"[PERF] 获取工具实例耗时: {(perf_tool_get - perf_parse) * 1000:.2f}ms")
            
            perf_exec_start = time.time()
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
            perf_exec_end = time.time()
            logger.info(f"[PERF] 工具 {tool_name} 执行耗时: {(perf_exec_end - perf_exec_start) * 1000:.2f}ms")

            # 添加工具结果消息
            perf_msg_start = time.time()
            self.add_message(
                "tool",
                content=tool_result,
                tool_call_id=tool_call_id
            )
            perf_msg_end = time.time()
            logger.info(f"[PERF] 添加工具结果消息耗时: {(perf_msg_end - perf_msg_start) * 1000:.2f}ms")

            total_tool_time = (perf_msg_end - tool_perf_start) * 1000
            logger.info(f"[PERF] 工具 {tool_name} 总耗时: {total_tool_time:.2f}ms")

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