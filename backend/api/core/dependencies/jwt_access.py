from fastapi import Depends, Query, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from api.core.exceptions import AppExceptions

from utils.jwt import JWT

from api.core.config import get_settings

settings = get_settings()


async def get_user_token(
    credentials: HTTPAuthorizationCredentials = Security(security := HTTPBearer()),
):
    token = credentials.credentials
    return await JWT.decode_jwt_token(token, "access")


def permission_required(
    required_permissions: list[str] = Query(None, include_in_schema=False)
):

    if not settings.ENABLE_PERMISSION_CHECK:

        async def skip_check_permission():
            return

        return Depends(skip_check_permission)

    async def permission_check(
        user_decode_token: dict[str, str] = Depends(get_user_token),
    ):
        permissions: list[str] | None = user_decode_token.get("permissions", [])
        required_user_permission = [
            permission
            for permission in permissions
            if permission in required_permissions
        ]
        if not required_user_permission:
            raise AppExceptions.forbidden_exception(
                "Forbidden: insufficient permissions"
            )
        return

    return Depends(permission_check)
