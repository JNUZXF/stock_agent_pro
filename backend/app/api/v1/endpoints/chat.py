"""
聊天API端点
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.chat_service import ChatService
from app.schemas.chat import ChatRequest, ChatChunkResponse
from app.core.security import get_current_user_id_or_default
from app.core.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat")
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id_or_default),
    db: Session = Depends(get_db)
):
    """
    聊天接口（流式输出）

    Args:
        request: 聊天请求
        user_id: 用户ID（从Token获取）
        db: 数据库会话

    Returns:
        Server-Sent Events流式响应
    """
    async def generate():
        """生成SSE流（真正的异步）"""
        chat_service = ChatService(db)

        try:
            # 使用异步流式输出
            async for response in chat_service.chat_stream_async(
                user_id=int(user_id),
                message=request.message,
                conversation_id=request.conversation_id,
                agent_type=request.agent_type
            ):
                # 转换为JSON并添加SSE格式
                data = response.model_dump_json()
                # 确保每个chunk都立即发送，不被缓冲
                chunk = f"data: {data}\n\n"
                # 使用bytes编码，确保立即发送
                yield chunk.encode('utf-8')

        except AgentExecutionError as e:
            logger.error(f"智能体执行失败: {str(e)}")
            error_response = ChatChunkResponse(
                type="error",
                error=str(e)
            )
            chunk = f"data: {error_response.model_dump_json()}\n\n"
            yield chunk.encode('utf-8')

        except Exception as e:
            logger.error(f"聊天失败: {str(e)}", exc_info=True)
            error_response = ChatChunkResponse(
                type="error",
                error=f"服务器错误: {str(e)}"
            )
            chunk = f"data: {error_response.model_dump_json()}\n\n"
            yield chunk.encode('utf-8')

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Content-Type-Options": "nosniff"
        }
    )
