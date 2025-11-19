from uuid import UUID

from api.core.config import get_settings
from api.core.exceptions import AppExceptions
from api.v1.roles.repo_interface import IRoleRepository
from api.v1.roles.schemas import Role
from api.v1.users.repo_interface import IUserRepository
from api.v1.users.schemas import CreateUser, User
from db.db_exceptions import DBException
from utils.hashing import Hasher

settings = get_settings()


class UserService:
    def __init__(
        self,
        user_repository_interface: IUserRepository,
        role_repository_interface: IRoleRepository,
    ):
        self._repo: IUserRepository = user_repository_interface
        self._role_repo: IRoleRepository = role_repository_interface

    async def get_user_by_id(self, user_id: UUID) -> User:
        try:
            user: User | None = await self._repo.get_by_id(user_id)
            if user is None:
                raise AppExceptions.not_found_exception("User with this id not found")
            return user
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def create_user_in_database(self, user_info: CreateUser) -> User:
        try:
            if (
                await self._repo.get_by_username(
                    user_info.username, exact_match=True, case_sensitive=False
                )
                != []
            ):
                raise AppExceptions.bad_request_exception(
                    f"User with username {user_info.username} already exists"
                )

            if user_info.role_ids:
                roles: dict[UUID, Role] = {
                    role.id: role for role in await self._role_repo.get_all()
                }
                for role_id in user_info.role_ids:
                    if not (role := roles.get(role_id, None)):
                        raise AppExceptions.bad_request_exception(
                            f"Role with id {role_id} not found"
                        )
                    if role.name == settings.SUPER_ROLE_NAME:
                        raise AppExceptions.forbidden_exception(
                            "Creating a superuser is forbidden"
                        )
            user_info.password = Hasher.get_password_hash(user_info.password)
            return await self._repo.create(user_info)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def update_user(self, user: User, body: CreateUser) -> User:
        try:
            body.password = (
                Hasher.get_password_hash(body.password) if body.password else None
            )
            if not (user_info := body.model_dump(exclude_none=True)):
                raise AppExceptions.validation_exception(
                    "At least one parameter must be defined"
                )
            if (
                user_info.get("username", None)
                and await self._repo.get_by_username(
                    user_info["username"], exact_match=True, case_sensitive=False
                )
                != []
            ):
                raise AppExceptions.bad_request_exception(
                    f"User with username {user_info['username']} already exists"
                )
            roles: list[Role] = await self._role_repo.get_all()
            user_role_names = [role.name for role in roles if role.id in user.role_ids]
            if settings.SUPER_ROLE_NAME in user_role_names:
                raise AppExceptions.forbidden_exception(
                    "User with super role is not allowed to perform this action"
                )
            return await self._repo.update(user, body)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def delete_user_by_id(self, user_id: UUID) -> UUID:
        try:
            user: User | None = await self._repo.get_by_id(user_id)
            if user is None:
                raise AppExceptions.not_found_exception("User with this id not found")
            roles: list[Role] = await self._role_repo.get_all()
            user_role_names = [role.name for role in roles if role.id in user.role_ids]
            if settings.SUPER_ROLE_NAME in user_role_names:
                raise AppExceptions.forbidden_exception(
                    "User with super role is not allowed to perform this action"
                )
            return await self._repo.delete(user_id)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def get_user_by_name_or_all(self, user_name: str) -> list[User]:
        try:
            if user_name:
                users = await self._repo.get_by_username(user_name)
                users += await self._repo.get_by_person_name_fields(user_name)
                return {user.id: user for user in users}.values()
            return await self._repo.get_all()
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")
