from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator

from config.validation import Validation


validator = Validation()


class TundeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class User(TundeModel):
    id: UUID
    username: str
    first_name: str
    last_name: str
    patronymic: str | None = None
    password: str | None = None
    finger_token: str | None = None
    role_ids: list[UUID] | None = []


class ShowUser(TundeModel):
    id: UUID
    username: str
    first_name: str
    last_name: str
    patronymic: str | None = None
    finger_token: str | None = None
    role_ids: list[UUID] | None = []


class CreateUser(BaseModel):
    username: str = Field(min_length=1, max_length=99)
    first_name: str = Field(min_length=1, max_length=99)
    last_name: str = Field(min_length=1, max_length=99)
    patronymic: str | None = None
    password: str | None = None
    finger_token: str | None = None
    role_ids: list[UUID] | None = []

    @field_validator("password")
    def validate_password(cls, value):
        pass_validation = validator.validate_password(value)
        if not pass_validation[0]:
            raise ValueError(pass_validation[1])
        if len(value) > 99:
            raise ValueError("Field length must be <= 99 characters")
        return value

    @field_validator("patronymic")
    def validate_patronymic(cls, value):
        if value is None:
            return None
        if len(value) > 99:
            raise ValueError("Field length must be <= 99 characters")
        return value.strip()

    @field_validator("finger_token")
    def validate_finger_token(cls, value):
        if value is None:
            return None
        if len(value) > 64:
            raise ValueError("Field length must be <= 64 characters")
        return value.strip()


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
        if value is None:
            return value
        pass_validation = validator.validate_password(value)
        if not pass_validation[0]:
            raise ValueError(pass_validation[1])
        if len(value) > 99:
            raise ValueError("Field length must be <= 99 characters")
        return value

    @field_validator("username", "first_name", "last_name")
    def not_empty(cls, value):
        if value is None:
            return value
        if not value.strip():
            raise ValueError("Field cannot be empty")
        if len(value) > 99:
            raise ValueError("Field length must be <= 99 characters")
        return value.strip()

    @field_validator("patronymic")
    def validate_patronymic(cls, value):
        if value is None:
            return None
        if len(value) > 99:
            raise ValueError("Field length must be <= 99 characters")
        return value.strip()

    @field_validator("finger_token")
    def validate_finger_token(cls, value):
        if value is None:
            return None
        if len(value) > 64:
            raise ValueError("Field length must be <= 64 characters")
        return value.strip()
