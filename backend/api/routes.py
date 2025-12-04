# backend/api/routes.py
# FastAPI路由定义，处理HTTP请求

import json
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Generator
import sys
import os
# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.models import (
    ChatRequest, 
    ChatChunkResponse, 
    ConversationsResponse,
    ConversationSummary,
    ConversationDetail,
    Message,
    ErrorResponse
)
from services.agent_service import agent_service


router = APIRouter(prefix="/api", tags=["chat"])


def format_sse_data(data: dict) -> bytes:
    """
    格式化SSE数据
    
    Args:
        data: 要发送的数据字典
        
    Returns:
        格式化的SSE字节串
    """
    json_str = json.dumps(data, ensure_ascii=False)
    return f"data: {json_str}\n\n".encode('utf-8')


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    聊天接口，支持流式输出
    
    Args:
        request: 聊天请求
        
    Returns:
        SSE流式响应
    """
    try:
        # 获取或创建Agent实例
        agent = agent_service.get_or_create_agent(request.conversation_id)
        
        def generate_response() -> Generator[bytes, None, None]:
            """生成SSE流式响应"""
            try:
                # 流式调用Agent的chat方法
                for chunk in agent.chat(request.message):
                    # 发送数据块
                    response_data = ChatChunkResponse(
                        type="chunk",
                        content=chunk,
                        conversation_id=agent.conversation_id
                    )
                    yield format_sse_data(response_data.model_dump())
                
                # 发送完成信号
                done_data = ChatChunkResponse(
                    type="done",
                    conversation_id=agent.conversation_id
                )
                yield format_sse_data(done_data.model_dump())
                
            except Exception as e:
                # 发送错误信息
                error_data = ChatChunkResponse(
                    type="error",
                    error=str(e),
                    conversation_id=agent.conversation_id
                )
                yield format_sse_data(error_data.model_dump())
        
        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/conversations", response_model=ConversationsResponse)
async def get_conversations():
    """
    获取所有会话列表
    
    Returns:
        会话列表
    """
    try:
        conversations = []
        # files目录在backend目录下
        files_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files")
        
        if not os.path.exists(files_dir):
            return ConversationsResponse(conversations=[])
        
        # 遍历files目录下的所有会话文件夹
        for conversation_id in os.listdir(files_dir):
            conversation_path = os.path.join(files_dir, conversation_id)
            
            if not os.path.isdir(conversation_path):
                continue
            
            # 读取conversation.json获取会话信息
            json_path = os.path.join(conversation_path, "conversation.json")
            if not os.path.exists(json_path):
                continue
            
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    messages = json.load(f)
                
                # 提取第一条用户消息作为标题
                title = "新会话"
                summary = ""
                # 从会话ID提取日期（格式：YYYYMMDD-HHMMSS+随机数）
                date = conversation_id.split("-")[0] if "-" in conversation_id else ""
                # 提取完整的时间戳用于排序（格式：YYYYMMDD-HHMMSS）
                timestamp_str = "-".join(conversation_id.split("-")[:2]) if "-" in conversation_id else conversation_id
                
                for msg in messages:
                    if msg.get("role") == "user" and "content" in msg:
                        title = msg["content"][:30] + ("..." if len(msg["content"]) > 30 else "")
                        break
                
                # 提取最后一条助手消息作为摘要
                for msg in reversed(messages):
                    if msg.get("role") == "assistant" and "content" in msg:
                        summary = msg["content"][:100] + ("..." if len(msg["content"]) > 100 else "")
                        break
                
                conversations.append({
                    "id": conversation_id,
                    "title": title,
                    "date": date,
                    "summary": summary,
                    "timestamp": timestamp_str  # 用于排序的时间戳
                })
                
            except Exception as e:
                # 跳过无法解析的会话
                continue
        
        # 按时间戳倒序排列（最新的在最前面）
        # 会话ID格式：YYYYMMDD-HHMMSS+随机数，按完整ID倒序排序即可
        conversations.sort(key=lambda x: x["id"], reverse=True)
        
        # 转换为ConversationSummary模型
        conversation_summaries = [
            ConversationSummary(
                id=conv["id"],
                title=conv["title"],
                date=conv["date"],
                summary=conv["summary"]
            )
            for conv in conversations
        ]
        
        return ConversationsResponse(conversations=conversation_summaries)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话列表失败: {str(e)}")


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str):
    """
    获取特定会话的详细记录
    
    Args:
        conversation_id: 会话ID
        
    Returns:
        会话详情
    """
    try:
        files_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "files")
        json_path = os.path.join(files_dir, conversation_id, "conversation.json")
        
        if not os.path.exists(json_path):
            raise HTTPException(status_code=404, detail="会话不存在")
        
        with open(json_path, "r", encoding="utf-8") as f:
            messages_data = json.load(f)
        
        # 转换为Message模型
        messages = []
        for msg in messages_data:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            
            # 跳过system消息和function_call相关消息
            if role in ["user", "assistant"] and content:
                messages.append(Message(role=role, content=content))
        
        return ConversationDetail(
            id=conversation_id,
            messages=messages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话详情失败: {str(e)}")

