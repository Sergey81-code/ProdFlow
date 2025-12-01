from uuid import UUID
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field, field_validator

from api.v1.users.schemas import User


class TundeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Role(TundeModel):
    id: UUID
    name: str
    permissions: list[str] = []

    users: list[User] | None = None


class ShowRole(TundeModel):
    id: UUID
    name: str
    permissions: list[str] = []

    users: list[User] | None = None


class CreateRole(BaseModel):
    name: str = Field(min_length=1)
    permissions: list[str] = []


class UpdateRole(BaseModel):
    name: str | None = None
    permissions: list[str] | None = None

    @field_validator("name")
    def not_empty(cls, value):
        if value is None:
            return value
        if not value.strip():
            raise ValueError("Field cannot be empty")
        return value.strip()
