"""
数据库模型基类
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin:
    """时间戳混入类"""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BaseModel(TimestampMixin):
    """基础模型类"""

    @declared_attr
    def __tablename__(cls):
        """自动生成表名（类名的小写复数形式）"""
        return cls.__name__.lower() + "s"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
