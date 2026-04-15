from typing import cast

from app.core.exceptions.api_exceptions import ApiExceptions
from app.users.models import User
from app.users.repo_interface import IUserRepository
from utils.jwt import JWT


class AuthService:
    def __init__(self, repo: IUserRepository):
        self._repo: IUserRepository = repo

    async def _authenticate_user(self, username: str, password: str) -> User:
        if not (
            users := cast(
                list[User],
                await self._repo.get_by_username(
                    username,
                    exact_match=True,
                    case_sensitive=True,
                ),
            )
        ):
            raise ApiExceptions.unauthorized_exception("Incorrect username or password")
        if password != users[0].password:
            raise ApiExceptions.unauthorized_exception("Incorrect username or password")
        return users[0]

    async def create_access_token(self, username: str, password: str):
        user: User = await self._authenticate_user(username, password)
        permissions = await self._repo.get_user_permissions(user.id)
        return await JWT.create_jwt_token(
            data={
                "sub": user.username,
                "user_id": str(user.id),
                "roles": [str(role.id) for role in user.roles],
                "permissions": permissions,
            },
            token_type="access",
        )
