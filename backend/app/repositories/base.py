"""
基础Repository类
提供通用的CRUD操作
"""
from typing import Generic, TypeVar, Type, List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.db.session import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """基础Repository类"""

    def __init__(self, model: Type[ModelType], db: Session):
        """
        初始化Repository

        Args:
            model: SQLAlchemy模型类
            db: 数据库会话
        """
        self.model = model
        self.db = db

    def get(self, id: int) -> Optional[ModelType]:
        """
        根据ID获取单个对象

        Args:
            id: 对象ID

        Returns:
            模型对象或None
        """
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        获取多个对象

        Args:
            skip: 跳过的记录数
            limit: 返回的最大记录数
            order_by: 排序字段

        Returns:
            模型对象列表
        """
        query = self.db.query(self.model)

        if order_by:
            if order_by.startswith("-"):
                # 降序
                query = query.order_by(desc(getattr(self.model, order_by[1:])))
            else:
                # 升序
                query = query.order_by(getattr(self.model, order_by))

        return query.offset(skip).limit(limit).all()

    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """
        创建对象

        Args:
            obj_in: 对象数据字典

        Returns:
            创建的模型对象
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> ModelType:
        """
        更新对象

        Args:
            db_obj: 数据库对象
            obj_in: 更新数据字典

        Returns:
            更新后的模型对象
        """
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> bool:
        """
        删除对象

        Args:
            id: 对象ID

        Returns:
            是否删除成功
        """
        obj = self.get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

    def count(self) -> int:
        """
        统计对象数量

        Returns:
            对象总数
        """
        return self.db.query(self.model).count()

    def exists(self, id: int) -> bool:
        """
        检查对象是否存在

        Args:
            id: 对象ID

        Returns:
            是否存在
        """
        return self.db.query(self.model).filter(self.model.id == id).first() is not None
