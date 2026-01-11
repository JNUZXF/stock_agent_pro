"""
认证服务
"""
import logging
from datetime import timedelta
from sqlalchemy.orm import Session

from app.services.user_service import UserService
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.config import settings
from app.core.exceptions import InvalidTokenError, ResourceAlreadyExistsError
from app.schemas.auth import UserRegister, TokenResponse
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务"""

    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def register(self, register_data: UserRegister) -> TokenResponse:
        """
        用户注册

        Args:
            register_data: 注册数据

        Returns:
            Token响应

        Raises:
            ResourceAlreadyExistsError: 用户已存在
        """
        # 创建用户
        user_create = UserCreate(
            username=register_data.username,
            email=register_data.email,
            password=register_data.password,
            is_superuser=False
        )

        user = self.user_service.create_user(user_create)

        # 生成Token
        token_data = {"sub": str(user.id), "username": user.username}

        access_token = create_access_token(
            token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        refresh_token = create_refresh_token(
            token_data,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        logger.info(f"用户注册成功: {user.username}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    def login(self, username: str, password: str) -> TokenResponse:
        """
        用户登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            Token响应

        Raises:
            InvalidCredentialsError: 凭据无效
        """
        # 验证用户
        user = self.user_service.authenticate_user(username, password)

        # 生成Token
        token_data = {"sub": str(user.id), "username": user.username}

        access_token = create_access_token(
            token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        refresh_token = create_refresh_token(
            token_data,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        logger.info(f"用户登录成功: {user.username}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """
        刷新Token

        Args:
            refresh_token: 刷新Token

        Returns:
            新的Token响应

        Raises:
            InvalidTokenError: Token无效
        """
        # 验证刷新Token
        payload = verify_token(refresh_token, token_type="refresh")

        user_id = payload.get("sub")
        username = payload.get("username")

        # 生成新的Token
        token_data = {"sub": user_id, "username": username}

        access_token = create_access_token(
            token_data,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        new_refresh_token = create_refresh_token(
            token_data,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        logger.info(f"刷新Token成功: user_id={user_id}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
