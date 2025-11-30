import uuid
from typing import Annotated

from sqlalchemy import ARRAY, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from uuid_extensions import uuid7


class Base(DeclarativeBase):
    pass


uuid_pk = Annotated[
    uuid.UUID, mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid7)
]


class Department(Base):
    __tablename__ = "departmnets"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(128), unique=True, nullable=True)

    users: Mapped[list["User"]] = relationship(
        back_populates="department", lazy="selectin"
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    permissions: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    users: Mapped[list["User"]] = relationship(
        secondary="user_roles", back_populates="roles", lazy="selectin"
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid_pk]
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    patronymic: Mapped[str] = mapped_column(String(100), nullable=True)
    password: Mapped[str] = mapped_column(String(100), nullable=True)
    employee_number: Mapped[str] = mapped_column(String(100), nullable=True)
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departmnets.id", ondelete="SET NULL"),
        nullable=True,
    )

    department: Mapped["Department"] = relationship(
        back_populates="users", lazy="joined"
    )

    roles: Mapped[list["Role"]] = relationship(
        secondary="user_roles", back_populates="users", lazy="joined"
    )

    full_name_tsv: Mapped[str] = mapped_column(TSVECTOR, nullable=True)

    __table_args__ = (
        Index("idx_users_full_name_tsv", "full_name_tsv", postgresql_using="gin"),
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"), primary_key=True)


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    android_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    __table_args__ = (
        Index("ix_devices_android_id_hash", "android_id", postgresql_using="hash"),
    )
