from sqlalchemy.orm import DeclarativeBase

from app.common.driver import *


class BaseDB(DeclarativeBase):
    """定义基础类"""
    pass


class BaseDBModel(BaseDB):
    """定义base抽象类"""

    __abstract__ = True

    create_time: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP,
        default=func.current_timestamp(),
        comment="创建时间"
    )

    update_time: Mapped[TIMESTAMP] = mapped_column(
        TIMESTAMP,
        default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        comment="更新时间"
    )

    is_delete: Mapped[int] = mapped_column(
        TINYINT(1),
        nullable=False,
        default=0,
        comment="逻辑删除, 0-未删除, 1-已删除"
    )

    operator: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        comment="操作者"
    )









