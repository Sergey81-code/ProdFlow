from uuid import UUID
from pydantic import BaseModel, ConfigDict


class Role(BaseModel):
    id: UUID
    name: str
    permissions: list[str] = []


class TundeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ShowRole(TundeModel):
    id: UUID
    name: str
    permissions: list[str] = []


class CreateRole(BaseModel):
    name: str
    permissions: list[str] = []


class UpdateRole(BaseModel):
    name: str | None = None
    permissions: list[str] | None = None
