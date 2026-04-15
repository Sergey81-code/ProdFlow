from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.users.models import User


class Department(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    code: str

    users: list[User] | None = None
