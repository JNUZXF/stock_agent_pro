"""
安全认证模块
包含JWT Token生成/验证、密码哈希等功能
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import settings
from app.core.exceptions import InvalidTokenError, TokenExpiredError


# 密码哈希上下文
# 使用bcrypt作为主要方案，如果失败则回退到pbkdf2_sha256
import logging
_logger = logging.getLogger(__name__)

# bcrypt密码最大长度限制（字节）
BCRYPT_MAX_PASSWORD_LENGTH = 72

# 初始化密码哈希上下文
# 优先使用bcrypt，如果失败则回退到pbkdf2_sha256
_bcrypt_available = False
try:
    # 尝试初始化bcrypt
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # 使用一个短密码进行测试，避免触发72字节限制错误
    # 这个测试会触发passlib的内部检测逻辑
    try:
        test_hash = pwd_context.hash("test")
        pwd_context.verify("test", test_hash)
        _bcrypt_available = True
        _logger.info("bcrypt密码哈希方案初始化成功")
    except (ValueError, AttributeError) as test_error:
        # 如果测试失败（可能是版本兼容性问题），回退到pbkdf2_sha256
        _logger.warning(f"bcrypt测试失败: {str(test_error)}，使用pbkdf2_sha256作为密码哈希方案")
        pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        _bcrypt_available = False
    except Exception as test_error:
        # 捕获其他可能的异常
        _logger.warning(f"bcrypt测试出现未知错误: {str(test_error)}，使用pbkdf2_sha256作为密码哈希方案")
        pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        _bcrypt_available = False
except Exception as e:
    # 如果bcrypt初始化失败，使用pbkdf2_sha256作为备选
    _logger.warning(f"bcrypt初始化失败: {str(e)}，使用pbkdf2_sha256作为密码哈希方案")
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    _bcrypt_available = False

# HTTP Bearer认证
security = HTTPBearer()


class PasswordHandler:
    """密码处理器"""

    @staticmethod
    def _preprocess_password(password: str) -> str:
        """
        预处理密码，确保不超过bcrypt的72字节限制
        
        如果密码超过72字节，先使用SHA256哈希，然后再用bcrypt哈希
        这样可以保持安全性，同时避免bcrypt的长度限制
        
        Args:
            password: 原始密码
            
        Returns:
            预处理后的密码（字符串，不超过72字节）
        """
        password_bytes = password.encode('utf-8')
        
        # 如果密码长度超过72字节，先使用SHA256哈希
        if len(password_bytes) > BCRYPT_MAX_PASSWORD_LENGTH:
            # 使用SHA256哈希，然后转换为十六进制字符串（64字符）
            sha256_hash = hashlib.sha256(password_bytes).hexdigest()
            return sha256_hash
        
        return password

    @staticmethod
    def hash_password(password: str) -> str:
        """
        哈希密码
        
        Args:
            password: 原始密码
            
        Returns:
            哈希后的密码
        """
        # 预处理密码，确保不超过bcrypt限制
        processed_password = PasswordHandler._preprocess_password(password)
        
        try:
            return pwd_context.hash(processed_password)
        except (ValueError, AttributeError) as e:
            # 如果bcrypt失败（例如密码长度问题或版本兼容性问题），回退到pbkdf2_sha256
            if _bcrypt_available:
                _logger.warning(f"bcrypt哈希失败: {str(e)}，回退到pbkdf2_sha256")
                # 创建使用pbkdf2_sha256的上下文
                fallback_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
                return fallback_context.hash(processed_password)
            raise
        except Exception as e:
            # 捕获其他可能的异常
            if _bcrypt_available:
                _logger.warning(f"bcrypt哈希出现未知错误: {str(e)}，回退到pbkdf2_sha256")
                fallback_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
                return fallback_context.hash(processed_password)
            raise

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        验证密码
        
        Args:
            plain_password: 明文密码
            hashed_password: 哈希后的密码
            
        Returns:
            是否匹配
        """
        # 预处理密码，确保与哈希时使用相同的处理方式
        processed_password = PasswordHandler._preprocess_password(plain_password)
        
        try:
            return pwd_context.verify(processed_password, hashed_password)
        except (ValueError, AttributeError) as e:
            # 如果bcrypt验证失败，尝试使用pbkdf2_sha256
            if _bcrypt_available:
                try:
                    fallback_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
                    return fallback_context.verify(processed_password, hashed_password)
                except Exception:
                    return False
            return False
        except Exception as e:
            # 捕获其他可能的异常
            if _bcrypt_available:
                try:
                    fallback_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
                    return fallback_context.verify(processed_password, hashed_password)
                except Exception:
                    return False
            return False


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


async def get_current_user_id_or_default(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> str:
    """
    从Token中获取当前用户ID，如果没有则返回默认用户ID
    
    注意：此函数会延迟导入数据库依赖，避免循环导入

    Args:
        credentials: HTTP认证凭据（可选）

    Returns:
        用户ID（字符串）
    """
    # 如果有认证凭据，尝试获取用户ID
    if credentials is not None:
        try:
            return await get_current_user_id(credentials)
        except HTTPException:
            pass  # 如果token无效，继续使用默认用户
    
    # 获取或创建默认用户（延迟导入避免循环依赖）
    from app.db.session import SessionLocal
    from app.services.user_service import UserService
    from app.schemas.user import UserCreate
    
    # 创建数据库会话
    db = SessionLocal()
    try:
        user_service = UserService(db)
        
        # 查找默认用户（用户名：guest）
        default_user = user_service.get_user_by_username("guest")
        
        if default_user is None:
            # 创建默认用户
            default_user = user_service.create_user(
                UserCreate(
                    username="guest",
                    email="guest@example.com",
                    password="guest_password_change_me",
                    is_superuser=False
                )
            )
        
        return str(default_user.id)
    finally:
        db.close()


# 导出便捷函数
hash_password = PasswordHandler.hash_password
verify_password = PasswordHandler.verify_password
create_access_token = TokenHandler.create_access_token
create_refresh_token = TokenHandler.create_refresh_token
decode_token = TokenHandler.decode_token
verify_token = TokenHandler.verify_token
