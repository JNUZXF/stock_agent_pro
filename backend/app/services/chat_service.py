"""
聊天服务
提供统一的聊天接口，协调智能体和数据库操作
"""
import logging
import asyncio
import time
from typing import Generator, Optional, AsyncGenerator
from datetime import datetime
from sqlalchemy.orm import Session
from concurrent.futures import ThreadPoolExecutor

from app.agents.manager import agent_manager
from app.services.conversation_service import ConversationService
from app.core.exceptions import AgentExecutionError
from app.schemas.conversation import ConversationCreate, MessageCreate
from app.schemas.chat import ChatChunkResponse

logger = logging.getLogger(__name__)

# 创建线程池用于执行数据库操作
_db_executor = ThreadPoolExecutor(max_workers=5)


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
        流式聊天（同步接口，内部调用异步实现）

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
        # 获取或创建事件循环
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # 使用异步生成器
        async_gen = self.chat_stream_async(user_id, message, conversation_id, agent_type)
        
        # 将异步生成器转换为同步生成器
        while True:
            try:
                chunk = loop.run_until_complete(async_gen.__anext__())
                yield chunk
            except StopAsyncIteration:
                break
    
    async def chat_stream_async(
        self,
        user_id: int,
        message: str,
        conversation_id: Optional[str] = None,
        agent_type: str = "stock_analysis"
    ) -> AsyncGenerator[ChatChunkResponse, None]:
        """
        异步流式聊天

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
        # 性能计时开始
        perf_timestamps = {}
        perf_timestamps['service_start'] = time.time()
        
        # 先快速生成conversation_id，不阻塞
        if not conversation_id:
            conversation_id = self._generate_conversation_id()
        perf_timestamps['conversation_id_generated'] = time.time()
        logger.info(f"[PERF] 生成conversation_id耗时: {(perf_timestamps['conversation_id_generated'] - perf_timestamps['service_start']) * 1000:.2f}ms")

        # 获取或创建智能体（这一步很快，不涉及数据库写入）
        agent = agent_manager.get_agent(
            user_id=str(user_id),
            conversation_id=conversation_id,
            agent_type=agent_type
        )
        perf_timestamps['agent_obtained'] = time.time()
        logger.info(f"[PERF] 获取智能体耗时: {(perf_timestamps['agent_obtained'] - perf_timestamps['conversation_id_generated']) * 1000:.2f}ms")

        # 立即开始流式输出，不等待数据库操作
        assistant_response = ""
        first_chunk_sent = False
        db_task = None
        perf_timestamps['before_agent_chat'] = time.time()
        logger.info(f"[PERF] 准备调用agent.chat_async，总耗时: {(perf_timestamps['before_agent_chat'] - perf_timestamps['service_start']) * 1000:.2f}ms")

        try:
            # 流式生成回复 - 立即开始，不等待数据库操作
            async for chunk in agent.chat_async(message):
                if not first_chunk_sent:
                    first_chunk_sent = True
                    perf_timestamps['first_chunk_received'] = time.time()
                    time_to_first_chunk = (perf_timestamps['first_chunk_received'] - perf_timestamps['service_start']) * 1000
                    logger.info(f"[PERF] ⚡ 首Token到达服务层耗时: {time_to_first_chunk:.2f}ms")
                    
                    # 第一个chunk到达时，在后台异步处理数据库操作（完全不阻塞）
                    db_task = asyncio.create_task(
                        self._save_conversation_and_user_message(
                            user_id, conversation_id, message
                        )
                    )

                assistant_response += chunk
                yield ChatChunkResponse(
                    type="chunk",
                    content=chunk,
                    conversation_id=conversation_id
                )

            # 等待数据库任务完成（如果还在运行）
            if db_task and not db_task.done():
                try:
                    await db_task
                except Exception as db_error:
                    logger.warning(f"数据库操作失败（不影响流式输出）: {db_error}")

            # 流式输出完成后，在后台保存助手回复到数据库
            asyncio.create_task(
                self._save_assistant_message(
                    user_id, conversation_id, assistant_response
                )
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

    async def _save_conversation_and_user_message(
        self,
        user_id: int,
        conversation_id: str,
        message: str
    ) -> None:
        """
        异步保存会话和用户消息（在线程池中执行）

        Args:
            user_id: 用户ID
            conversation_id: 会话ID
            message: 用户消息
        """
        loop = asyncio.get_event_loop()
        
        def _db_operation():
            try:
                # 快速检查会话是否存在，如果不存在则创建
                try:
                    self.conversation_service.get_conversation(conversation_id, user_id)
                except Exception:
                    # 会话不存在，创建新会话
                    conversation_data = ConversationCreate(
                        conversation_id=conversation_id,
                        title=message[:50] if len(message) <= 50 else message[:47] + "..."
                    )
                    self.conversation_service.create_conversation(
                        user_id=user_id,
                        conversation_data=conversation_data
                    )
                    logger.info(f"创建新会话: {conversation_id}")

                # 保存用户消息
                user_message = MessageCreate(
                    role="user",
                    content=message
                )
                self.conversation_service.add_message(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    message_data=user_message
                )
            except Exception as e:
                logger.warning(f"保存会话和用户消息失败: {e}")
        
        # 在线程池中执行数据库操作
        await loop.run_in_executor(_db_executor, _db_operation)
    
    async def _save_assistant_message(
        self,
        user_id: int,
        conversation_id: str,
        content: str
    ) -> None:
        """
        异步保存助手消息（在线程池中执行）

        Args:
            user_id: 用户ID
            conversation_id: 会话ID
            content: 助手回复内容
        """
        loop = asyncio.get_event_loop()
        
        def _db_operation():
            try:
                assistant_message = MessageCreate(
                    role="assistant",
                    content=content
                )
                self.conversation_service.add_message(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    message_data=assistant_message
                )
            except Exception as e:
                logger.warning(f"保存助手回复失败: {e}")
        
        # 在线程池中执行数据库操作
        await loop.run_in_executor(_db_executor, _db_operation)

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
