"""
用户数据模型
"""
from sqlalchemy import Column, String, Boolean, Integer
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.base import BaseModel


class User(Base, BaseModel):
    """用户模型"""

    __tablename__ = "users"

    # 基本信息
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    # 用户状态
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # 用户配额
    max_conversations = Column(Integer, default=100, nullable=False)
    max_messages_per_conversation = Column(Integer, default=100, nullable=False)

    # 关系
    conversations = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
