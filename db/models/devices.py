from sqlalchemy import Index, String
from sqlalchemy.orm import Mapped, mapped_column

from .core import Base, uuid_pk


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    android_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    __table_args__ = (
        Index("ix_devices_android_id_hash", "android_id", postgresql_using="hash"),
    )
