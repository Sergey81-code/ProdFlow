import uuid
from typing import Annotated

from sqlalchemy import ARRAY, Index, String
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid_extensions import uuid7


class Base(DeclarativeBase):
    pass


uuid_pk = Annotated[
    uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
]


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    permissions: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    patronymic: Mapped[str] = mapped_column(String(100), nullable=True)
    password: Mapped[str] = mapped_column(String(100), nullable=True)
    finger_token: Mapped[str] = mapped_column(String(100), nullable=True)
    role_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), default=list, nullable=True
    )

    full_name_tsv: Mapped[str] = mapped_column(TSVECTOR, nullable=True)

    __table_args__ = (
        Index("idx_users_full_name_tsv", "full_name_tsv", postgresql_using="gin"),
    )


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    android_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    __table_args__ = (
        Index("ix_devices_android_id_hash", "android_id", postgresql_using="hash"),
    )
