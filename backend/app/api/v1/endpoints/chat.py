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
        """生成SSE流"""
        chat_service = ChatService(db)

        try:
            for response in chat_service.chat_stream(
                user_id=int(user_id),
                message=request.message,
                conversation_id=request.conversation_id,
                agent_type=request.agent_type
            ):
                # 转换为JSON并添加SSE格式
                data = response.model_dump_json()
                yield f"data: {data}\n\n"

        except AgentExecutionError as e:
            logger.error(f"智能体执行失败: {str(e)}")
            error_response = ChatChunkResponse(
                type="error",
                error=str(e)
            )
            yield f"data: {error_response.model_dump_json()}\n\n"

        except Exception as e:
            logger.error(f"聊天失败: {str(e)}", exc_info=True)
            error_response = ChatChunkResponse(
                type="error",
                error=f"服务器错误: {str(e)}"
            )
            yield f"data: {error_response.model_dump_json()}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
