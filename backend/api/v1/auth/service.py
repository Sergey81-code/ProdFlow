from typing import cast
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppExceptions
from api.v1.users.repo_interface import IUserRepository
from api.v1.users.schemas import User
from utils.hashing import Hasher
from utils.jwt import JWT


class AuthService:

    def __init__(self, repo: IUserRepository):
        self._repo: IUserRepository = repo

    async def _authenticate_user(self, username: str, password: str) -> User:
        if not (
            user := cast(
                list[User],
                await self._repo.get_by_username(
                    username,
                    exact_match=True,
                    case_sensitive=True,
                ),
            )
        ):
            raise AppExceptions.unauthorized_exception("Incorrect username or password")
        if not Hasher.verify_password(password, user[0].password):
            raise AppExceptions.unauthorized_exception("Incorrect username or password")
        return user[0]

    async def create_access_token(self, username: str, password: str):
        user: User = await self._authenticate_user(username, password)
        permissions = await self._repo.get_user_permissions(user.id)
        return await JWT.create_jwt_token(
            data={
                "sub": user.username,
                "user_id": str(user.id),
                "roles": [str(role_id) for role_id in user.role_ids],
                "permissions": permissions,
            },
            token_type="access",
        )
