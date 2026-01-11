"""
消息数据模型
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.base import BaseModel


class Message(Base, BaseModel):
    """消息模型"""

    __tablename__ = "messages"

    # 对话关联
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # 消息内容
    role = Column(String(20), nullable=False)  # user, assistant, system, function
    content = Column(Text, nullable=True)

    # 功能调用相关（可选）
    function_call = Column(JSON, nullable=True)
    tool_calls = Column(JSON, nullable=True)

    # 元数据
    metadata = Column(JSON, nullable=True)

    # 关系
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, conversation_id={self.conversation_id})>"

    def to_dict(self) -> dict:
        """转换为字典"""
        result = {
            "role": self.role,
            "content": self.content,
        }

        if self.function_call:
            result["function_call"] = self.function_call

        if self.tool_calls:
            result["tool_calls"] = self.tool_calls

        if self.metadata:
            result["metadata"] = self.metadata

        return result
