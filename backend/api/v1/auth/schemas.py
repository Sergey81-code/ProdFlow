import re

from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import field_validator

from api.core.exceptions import AppExceptions
from config.validation import Validation

validator = Validation()


class LoginUser(BaseModel):
    name: EmailStr
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
