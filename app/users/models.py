from uuid import UUID
from pydantic import BaseModel, ConfigDict


class UserRole(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class User(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    first_name: str
    last_name: str
    patronymic: str | None = None
    password: str | None = None
    employee_number: str | None = None
    roles: list[UserRole] | None = []
    department_id: UUID | None = None
