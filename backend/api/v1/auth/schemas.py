from pydantic import BaseModel, Field, field_validator

from api.core.exceptions import AppExceptions
from config.validation import Validation

validator = Validation()


class LoginUser(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        pass_validation = validator.validate_password(value)
        if not pass_validation[0]:
            raise AppExceptions.unauthorized_exception(pass_validation[1])
        return value


class Token(BaseModel):
    access_token: str
    token_type: str
