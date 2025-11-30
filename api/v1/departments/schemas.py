from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class TundeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Department(TundeModel):
    id: UUID
    name: str
    code: str


class ShowDepartment(TundeModel):
    id: UUID
    name: str
    code: str


class CreateDepartment(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    code: str = Field(min_length=1, max_length=100)


class UpdateDepartment(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    code: str | None = Field(default=None, min_length=1, max_length=100)
