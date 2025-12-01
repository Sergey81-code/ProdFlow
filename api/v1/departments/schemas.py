from uuid import UUID
from typing import TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, Field


from api.v1.users.schemas import User


class TundeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Department(TundeModel):
    id: UUID
    name: str
    code: str

    users: list[User] | None = None


class ShowDepartment(TundeModel):
    id: UUID
    name: str
    code: str

    users: list[User] | None = None


class CreateDepartment(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=100)


class UpdateDepartment(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, min_length=1, max_length=100)
