from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator

from api.core.exceptions import AppExceptions
from config.validation import Validation


validator = Validation()


class User(BaseModel):
    id: UUID
    username: str
    first_name: str
    last_name: str
    patronymic: str | None = None
    password: str | None = None
    finger_token: str | None = None
    role_ids: list[UUID] = []


class TundeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ShowUser(TundeModel):
    id: UUID
    username: str
    first_name: str
    last_name: str
    patronymic: str | None = None
    finger_token: str | None = None
    role_ids: list[UUID] = []


class CreateUser(BaseModel):
    username: str
    first_name: str
    last_name: str
    patronymic: str | None = None
    password: str | None = None
    finger_token: str | None = None
    role_ids: list[UUID] = []

    @field_validator("password")
    def validate_password(cls, value):
        pass_validation = validator.validate_password(value)
        if not pass_validation[0]:
            raise AppExceptions.bad_request_exception(pass_validation[1])
        return value


class UpdateUser(BaseModel):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    patronymic: str | None = None
    role_ids: list[UUID] | None = None
    password: str | None = None
    finger_token: str | None = None

    @field_validator("password")
    def validate_password(cls, value):
        pass_validation = validator.validate_password(value)
        if not pass_validation[0]:
            raise AppExceptions.bad_request_exception(pass_validation[1])
        return value
