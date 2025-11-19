import datetime

from jose import JWTError, jwt

from api.core.config import get_settings
from api.core.exceptions import AppExceptions

settings = get_settings()


class JWT:
    @staticmethod
    async def create_jwt_token(
        data: dict,
        token_type: str = "access",
        expires_delta: datetime.timedelta | None = None,
    ) -> str:
        if token_type == "access":
            token_key = settings.SECRET_KEY_FOR_ACCESS
            token_time = settings.TOKEN_EXPIRE_MINUTES

        to_encode = data.copy()
        expire = datetime.datetime.now(datetime.timezone.utc) + (
            expires_delta or datetime.timedelta(minutes=token_time)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, token_key, algorithm=settings.ALGORITHM)

    @staticmethod
    async def decode_jwt_token(
        token: str, token_type: str = "access"
    ) -> dict[str, str]:
        if token_type == "access":
            token_key = settings.SECRET_KEY_FOR_ACCESS
        try:
            payload = jwt.decode(token, token_key, algorithms=[settings.ALGORITHM])
            if "sub" not in payload.keys():
                raise JWTError
        except JWTError:
            raise AppExceptions.unauthorized_exception("Could not validate credentials")
        return payload
