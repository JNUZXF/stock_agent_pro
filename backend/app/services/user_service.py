"""
用户服务
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password
from app.core.exceptions import (
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
    InvalidCredentialsError
)
from app.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """用户服务"""

    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def create_user(self, user_data: UserCreate) -> User:
        """
        创建用户

        Args:
            user_data: 用户数据

        Returns:
            创建的用户对象

        Raises:
            ResourceAlreadyExistsError: 用户名或邮箱已存在
        """
        # 检查用户名是否存在
        if self.repo.exists_by_username(user_data.username):
            raise ResourceAlreadyExistsError(
                f"用户名 '{user_data.username}' 已存在"
            )

        # 检查邮箱是否存在
        if self.repo.exists_by_email(user_data.email):
            raise ResourceAlreadyExistsError(
                f"邮箱 '{user_data.email}' 已被注册"
            )

        # 创建用户
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = hash_password(user_dict.pop("password"))

        user = self.repo.create(user_dict)

        logger.info(f"创建用户成功: {user.username} (ID: {user.id})")
        return user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            用户对象或None
        """
        return self.repo.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户

        Args:
            username: 用户名

        Returns:
            用户对象或None
        """
        return self.repo.get_by_username(username)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户

        Args:
            email: 邮箱

        Returns:
            用户对象或None
        """
        return self.repo.get_by_email(email)

    def authenticate_user(self, username: str, password: str) -> User:
        """
        验证用户凭据

        Args:
            username: 用户名
            password: 密码

        Returns:
            用户对象

        Raises:
            InvalidCredentialsError: 凭据无效
        """
        user = self.repo.get_by_username(username)

        if not user:
            raise InvalidCredentialsError("用户名或密码错误")

        if not user.is_active:
            raise InvalidCredentialsError("用户已被禁用")

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("用户名或密码错误")

        logger.info(f"用户认证成功: {username}")
        return user

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """
        更新用户信息

        Args:
            user_id: 用户ID
            user_data: 更新数据

        Returns:
            更新后的用户对象

        Raises:
            ResourceNotFoundError: 用户不存在
        """
        user = self.repo.get(user_id)

        if not user:
            raise ResourceNotFoundError(f"用户 ID {user_id} 不存在")

        # 只更新提供的字段
        update_dict = user_data.model_dump(exclude_unset=True)

        user = self.repo.update(user, update_dict)

        logger.info(f"更新用户信息: {user.username} (ID: {user.id})")
        return user

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """
        修改密码

        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码

        Returns:
            是否修改成功

        Raises:
            ResourceNotFoundError: 用户不存在
            InvalidCredentialsError: 旧密码错误
        """
        user = self.repo.get(user_id)

        if not user:
            raise ResourceNotFoundError(f"用户 ID {user_id} 不存在")

        # 验证旧密码
        if not verify_password(old_password, user.hashed_password):
            raise InvalidCredentialsError("旧密码错误")

        # 更新密码
        user.hashed_password = hash_password(new_password)
        self.db.commit()

        logger.info(f"修改密码成功: {user.username}")
        return True

    def deactivate_user(self, user_id: int) -> bool:
        """
        停用用户

        Args:
            user_id: 用户ID

        Returns:
            是否停用成功

        Raises:
            ResourceNotFoundError: 用户不存在
        """
        user = self.repo.get(user_id)

        if not user:
            raise ResourceNotFoundError(f"用户 ID {user_id} 不存在")

        user.is_active = False
        self.db.commit()

        logger.info(f"停用用户: {user.username} (ID: {user.id})")
        return True
