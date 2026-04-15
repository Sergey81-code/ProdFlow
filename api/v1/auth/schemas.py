from pydantic import BaseModel, Field, field_validator

from app.core.exceptions.api_exceptions import ApiExceptions
from config.validation import Validation

validator = Validation()


class LoginUser(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    password: str

    @field_validator("password")
    def validate_password(cls, value):
        pass_validation = validator.validate_password(value)
        if not pass_validation[0]:
            raise ApiExceptions.unauthorized_exception(pass_validation[1])
        return value


class Token(BaseModel):
    access_token: str
    token_type: str
