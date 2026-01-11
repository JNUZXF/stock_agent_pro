"""
用户Repository
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """用户Repository"""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户

        Args:
            username: 用户名

        Returns:
            用户对象或None
        """
        return self.db.query(User).filter(User.username == username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户

        Args:
            email: 邮箱

        Returns:
            用户对象或None
        """
        return self.db.query(User).filter(User.email == email).first()

    def exists_by_username(self, username: str) -> bool:
        """
        检查用户名是否存在

        Args:
            username: 用户名

        Returns:
            是否存在
        """
        return self.db.query(User).filter(User.username == username).first() is not None

    def exists_by_email(self, email: str) -> bool:
        """
        检查邮箱是否存在

        Args:
            email: 邮箱

        Returns:
            是否存在
        """
        return self.db.query(User).filter(User.email == email).first() is not None

    def get_active_users(self, skip: int = 0, limit: int = 100):
        """
        获取活跃用户列表

        Args:
            skip: 跳过的记录数
            limit: 返回的最大记录数

        Returns:
            用户列表
        """
        return (
            self.db.query(User)
            .filter(User.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
