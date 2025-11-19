from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TundeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Device(TundeModel):
    id: UUID
    name: str
    android_id: str


class ShowDevice(TundeModel):
    id: UUID
    name: str
    android_id: str


class CreateDevice(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    android_id: str = Field(min_length=1, max_length=255)


class UpdateDevice(BaseModel):
    name: str | None = None
    android_id: str | None = None

    @field_validator("name", "android_id")
    def not_empty(cls, value):
        if value is None:
            return value
        if not value.strip():
            raise ValueError("Field cannot be empty")
        if len(value) > 255:
            raise ValueError("Field length must be <= 256 characters")
        return value.strip()
