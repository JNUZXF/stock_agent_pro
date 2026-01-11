"""
中间件
"""
import time
import logging
from typing import Callable
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import StockAgentException

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        记录请求和响应日志

        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器

        Returns:
            响应对象
        """
        # 记录请求开始
        start_time = time.time()
        request_id = id(request)

        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - 开始处理"
        )

        try:
            # 调用下一个处理器
            response = await call_next(request)

            # 计算处理时间
            process_time = time.time() - start_time

            # 记录响应
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"状态码: {response.status_code}, 耗时: {process_time:.3f}s"
            )

            # 添加响应头
            response.headers["X-Process-Time"] = f"{process_time:.3f}"

            return response

        except Exception as e:
            # 计算处理时间
            process_time = time.time() - start_time

            # 记录错误
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"错误: {str(e)}, 耗时: {process_time:.3f}s",
                exc_info=True
            )

            raise


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """异常处理中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        统一处理异常

        Args:
            request: 请求对象
            call_next: 下一个中间件或路由处理器

        Returns:
            响应对象
        """
        try:
            return await call_next(request)

        except StockAgentException as e:
            # 自定义业务异常
            status_code = self._get_status_code(e)

            return JSONResponse(
                status_code=status_code,
                content={
                    "error_code": e.error_code,
                    "message": e.message,
                    "details": e.details
                }
            )

        except Exception as e:
            # 未处理的异常
            logger.error(f"未处理的异常: {str(e)}", exc_info=True)

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error_code": "InternalServerError",
                    "message": "服务器内部错误",
                    "details": {}
                }
            )

    @staticmethod
    def _get_status_code(exception: StockAgentException) -> int:
        """
        根据异常类型获取HTTP状态码

        Args:
            exception: 异常对象

        Returns:
            HTTP状态码
        """
        from app.core.exceptions import (
            AuthenticationError,
            AuthorizationError,
            ResourceNotFoundError,
            ResourceAlreadyExistsError,
            ValidationError,
            RateLimitExceededError
        )

        if isinstance(exception, AuthenticationError):
            return status.HTTP_401_UNAUTHORIZED
        elif isinstance(exception, AuthorizationError):
            return status.HTTP_403_FORBIDDEN
        elif isinstance(exception, ResourceNotFoundError):
            return status.HTTP_404_NOT_FOUND
        elif isinstance(exception, ResourceAlreadyExistsError):
            return status.HTTP_409_CONFLICT
        elif isinstance(exception, ValidationError):
            return status.HTTP_422_UNPROCESSABLE_ENTITY
        elif isinstance(exception, RateLimitExceededError):
            return status.HTTP_429_TOO_MANY_REQUESTS
        else:
            return status.HTTP_500_INTERNAL_SERVER_ERROR
