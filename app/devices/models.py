from uuid import UUID
from pydantic import BaseModel, ConfigDict


class Device(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    android_id: str
