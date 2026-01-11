"""
自定义异常类
提供细粒度的错误处理
"""
from typing import Any, Dict, Optional


class StockAgentException(Exception):
    """基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


# 认证和授权异常
class AuthenticationError(StockAgentException):
    """认证失败"""
    pass


class AuthorizationError(StockAgentException):
    """授权失败"""
    pass


class TokenExpiredError(AuthenticationError):
    """Token过期"""
    pass


class InvalidTokenError(AuthenticationError):
    """无效Token"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """凭据无效"""
    pass


# 资源异常
class ResourceNotFoundError(StockAgentException):
    """资源不存在"""
    pass


class ResourceAlreadyExistsError(StockAgentException):
    """资源已存在"""
    pass


class ResourceLimitExceededError(StockAgentException):
    """资源限制超出"""
    pass


# 业务逻辑异常
class ValidationError(StockAgentException):
    """数据验证失败"""
    pass


class BusinessLogicError(StockAgentException):
    """业务逻辑错误"""
    pass


# 智能体异常
class AgentError(StockAgentException):
    """智能体错误"""
    pass


class AgentNotFoundError(AgentError):
    """智能体不存在"""
    pass


class AgentInitializationError(AgentError):
    """智能体初始化失败"""
    pass


class AgentExecutionError(AgentError):
    """智能体执行失败"""
    pass


# 工具异常
class ToolError(StockAgentException):
    """工具错误"""
    pass


class ToolNotFoundError(ToolError):
    """工具不存在"""
    pass


class ToolExecutionError(ToolError):
    """工具执行失败"""
    pass


class ToolValidationError(ToolError):
    """工具参数验证失败"""
    pass


# 外部服务异常
class ExternalServiceError(StockAgentException):
    """外部服务错误"""
    pass


class AIServiceError(ExternalServiceError):
    """AI服务错误"""
    pass


class DatabaseError(ExternalServiceError):
    """数据库错误"""
    pass


class CacheError(ExternalServiceError):
    """缓存错误"""
    pass


# 限流异常
class RateLimitExceededError(StockAgentException):
    """超出限流"""
    pass


# 配置异常
class ConfigurationError(StockAgentException):
    """配置错误"""
    pass
