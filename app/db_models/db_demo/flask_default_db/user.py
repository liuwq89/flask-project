import uuid

from app.common.driver import *
from app.db_models.base_model import BaseDBModel


def default_nick_name():
    """
    生成默认的nick_name
    """
    return f"用户{uuid.uuid4()[:8]}"


class UserModel(BaseDBModel):
    __tablename__ = "t_user"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键",
    )

    uuid: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        default=lambda: str(uuid.uuid4()),
        comment="用户的唯一uuid",
    )

    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="用户的手机号"
    )

    password: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="用户的hash密码",
    )

    real_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="用户的真实名称",
    )

    nick_name: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        default=default_nick_name,
        comment="用户的昵称",
    )

    other_info: Mapped[dict] = mapped_column(
        JSON,
        nullable=True,
        comment="用户的其他信息",
    )

    



