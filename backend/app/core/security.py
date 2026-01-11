"""
安全认证模块
包含JWT Token生成/验证、密码哈希等功能
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.core.exceptions import InvalidTokenError, TokenExpiredError


# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer认证
security = HTTPBearer()


class PasswordHandler:
    """密码处理器"""

    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)


class TokenHandler:
    """JWT Token处理器"""

    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建访问Token

        Args:
            data: Token载荷数据
            expires_delta: 过期时间增量

        Returns:
            JWT Token字符串
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def create_refresh_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建刷新Token

        Args:
            data: Token载荷数据
            expires_delta: 过期时间增量

        Returns:
            JWT Token字符串
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """
        解码Token

        Args:
            token: JWT Token字符串

        Returns:
            Token载荷数据

        Raises:
            InvalidTokenError: Token无效
            TokenExpiredError: Token过期
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Token已过期")
        except JWTError as e:
            raise InvalidTokenError(f"Token无效: {str(e)}")

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        验证Token类型

        Args:
            token: JWT Token字符串
            token_type: Token类型（access或refresh）

        Returns:
            Token载荷数据

        Raises:
            InvalidTokenError: Token类型不匹配
        """
        payload = TokenHandler.decode_token(token)

        if payload.get("type") != token_type:
            raise InvalidTokenError(f"期望{token_type} token，但收到{payload.get('type')} token")

        return payload


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    从Token中获取当前用户ID

    Args:
        credentials: HTTP认证凭据

    Returns:
        用户ID

    Raises:
        HTTPException: 认证失败
    """
    try:
        token = credentials.credentials
        payload = TokenHandler.verify_token(token, token_type="access")
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except (InvalidTokenError, TokenExpiredError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[str]:
    """
    从Token中获取当前用户ID（可选）

    Args:
        credentials: HTTP认证凭据（可选）

    Returns:
        用户ID或None
    """
    if credentials is None:
        return None

    try:
        return await get_current_user_id(credentials)
    except HTTPException:
        return None


# 导出便捷函数
hash_password = PasswordHandler.hash_password
verify_password = PasswordHandler.verify_password
create_access_token = TokenHandler.create_access_token
create_refresh_token = TokenHandler.create_refresh_token
decode_token = TokenHandler.decode_token
verify_token = TokenHandler.verify_token
