from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.users.models import User


class Role(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    permissions: list[str] = []

    users: list[User] | None = None
