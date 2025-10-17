from uuid import UUID
from pydantic import BaseModel


class Device(BaseModel):
    id: UUID
    name: str
    android_id: str


class TundeModel(BaseModel):
    class ConfigDict:
        from_attributes = True


class ShowDevice(TundeModel):
    id: UUID
    name: str
    android_id: str


class CreateDevice(BaseModel):
    name: str
    android_id: str


class UpdateDevice(BaseModel):
    name: str | None = None
    android_id: str | None = None
