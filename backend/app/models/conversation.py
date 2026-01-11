"""
对话数据模型
"""
from sqlalchemy import Column, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.base import BaseModel


class Conversation(Base, BaseModel):
    """对话模型"""

    __tablename__ = "conversations"

    # 基本信息
    conversation_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)

    # 用户关联
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # 统计信息
    message_count = Column(Integer, default=0, nullable=False)

    # 关系
    user = relationship("User", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, conversation_id={self.conversation_id}, user_id={self.user_id})>"
