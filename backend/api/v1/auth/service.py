from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppExceptions
from api.v1.users.repo_interface import UserRepoInterface
from api.v1.users.schemas import User
from utils.hashing import Hasher
from utils.jwt import JWT


class AuthService:

    def __init__(self, repo: UserRepoInterface):
        self._repo: UserRepoInterface = repo

    async def _authenticate_user(
        self, username: str, password: str, session: AsyncSession
    ) -> User:
        user: User = await self._repo.get_by_name(username)
        if user is not None:
            if not Hasher.verify_password(password, user.password):
                raise AppExceptions.unauthorized_exception(
                    "Incorrect username or password"
                )
        return user

    async def create_access_token(self, username: str, password: str):
        user: User = await self._authenticate_user(username, password)
        permissions = await self._repo.get_user_permissions(user.id)
        return await JWT.create_jwt_token(
            data={
                "sub": user.username,
                "user_id": str(user.id),
                "roles": user.role_ids,
                "permissions": permissions,
            },
            token_type="access",
        )
