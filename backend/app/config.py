"""
应用配置管理
支持多环境配置（开发、测试、生产）
"""
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, model_validator
import os
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置类"""

    # 应用基础配置
    APP_NAME: str = "Stock Agent Pro"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # API配置
    API_V1_PREFIX: str = "/api/v1"
    API_V2_PREFIX: str = "/api/v2"

    # 服务器配置
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=1, env="WORKERS")

    # CORS配置
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS: List[str] = ["*"]

    # 数据库配置
    DATABASE_URL: str = Field(
        default="sqlite:///./stock_agent.db",
        env="DATABASE_URL"
    )
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")
    DATABASE_POOL_SIZE: int = Field(default=5, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")

    # Redis配置（可选，用于缓存和会话）
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    REDIS_ENABLED: bool = Field(default=False, env="REDIS_ENABLED")

    # JWT认证配置
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        env="SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")

    # AI模型配置
    # 支持 AI_API_KEY 和 DOUBAO_API_KEY 两种环境变量名称
    AI_API_KEY: Optional[str] = Field(default=None, env="AI_API_KEY")
    
    @property
    def effective_ai_api_key(self) -> Optional[str]:
        """获取有效的AI API密钥（支持DOUBAO_API_KEY作为备选）"""
        import os
        return self.AI_API_KEY or os.getenv("DOUBAO_API_KEY")
    AI_BASE_URL: str = Field(
        default="https://ark.cn-beijing.volces.com/api/v3",
        env="AI_BASE_URL"
    )
    AI_MODEL: str = Field(
        default="doubao-seed-1-6-251015",
        env="AI_MODEL"
    )
    AI_FLASH_MODEL: str = Field(
        default="doubao-seed-1-6-flash",
        env="AI_FLASH_MODEL"
    )
    AI_MAX_TOKENS: int = Field(default=4096, env="AI_MAX_TOKENS")
    AI_TEMPERATURE: float = Field(default=0.7, env="AI_TEMPERATURE")
    AI_TIMEOUT: int = Field(default=60, env="AI_TIMEOUT")

    # 会话配置
    MAX_CONVERSATION_HISTORY: int = Field(default=50, env="MAX_CONVERSATION_HISTORY")
    CONVERSATION_TIMEOUT_MINUTES: int = Field(default=30, env="CONVERSATION_TIMEOUT_MINUTES")
    MAX_ACTIVE_AGENTS_PER_USER: int = Field(default=5, env="MAX_ACTIVE_AGENTS_PER_USER")

    # 文件存储配置
    FILES_DIR: str = Field(default="./files", env="FILES_DIR")
    MAX_FILE_SIZE_MB: int = Field(default=10, env="MAX_FILE_SIZE_MB")

    # 日志配置
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[str] = Field(default=None, env="LOG_FILE")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 限流配置
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_BURST: int = Field(default=10, env="RATE_LIMIT_BURST")

    # 监控配置
    METRICS_ENABLED: bool = Field(default=True, env="METRICS_ENABLED")
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """解析CORS origins"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @model_validator(mode="after")
    def validate_secret_key(self):
        """验证生产环境必须修改密钥"""
        if self.ENVIRONMENT == "production" and self.SECRET_KEY == "your-secret-key-change-in-production":
            raise ValueError("生产环境必须设置安全的SECRET_KEY")
        return self

    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.ENVIRONMENT == "development"

    @property
    def sqlalchemy_database_uri(self) -> str:
        """获取SQLAlchemy数据库URI"""
        return self.DATABASE_URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 导出配置实例
settings = get_settings()
