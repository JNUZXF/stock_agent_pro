"""
日志配置
"""
import logging
import sys
from typing import Optional

from app.config import settings


def setup_logging(log_level: Optional[str] = None, log_file: Optional[str] = None) -> None:
    """
    配置日志系统

    Args:
        log_level: 日志级别（默认从配置读取）
        log_file: 日志文件路径（默认从配置读取）
    """
    # 确定日志级别
    level = log_level or settings.LOG_LEVEL
    log_level_value = getattr(logging, level.upper(), logging.INFO)

    # 创建格式化器
    formatter = logging.Formatter(
        fmt=settings.LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level_value)

    # 移除现有的处理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level_value)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 添加文件处理器（如果配置了）
    file_path = log_file or settings.LOG_FILE
    if file_path:
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setLevel(log_level_value)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # 配置第三方库的日志级别
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

    logging.info(f"日志系统初始化完成: level={level}, file={file_path or 'None'}")
