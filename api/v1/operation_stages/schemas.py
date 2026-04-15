from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class TundeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ShowOperationStage(TundeModel):
    id: UUID
    name: str


class CreateOperationStage(BaseModel):
    name: str = Field(min_length=1, max_length=64)


class UpdateOperationStage(BaseModel):
    name: str = Field(default=None, min_length=1, max_length=64)
