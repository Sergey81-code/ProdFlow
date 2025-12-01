from uuid import UUID

from api.core.config import get_settings
from api.core.exceptions import AppExceptions
from api.v1.roles.repo_interface import IRoleRepository
from api.v1.roles.schemas import Role
from api.v1.users.repo_interface import IUserRepository
from api.v1.users.schemas import CreateUser, User
from db.db_exceptions import DBException

settings = get_settings()


class UserService:
    def __init__(
        self,
        user_repository_interface: IUserRepository,
        role_repository_interface: IRoleRepository,
    ):
        self._repo: IUserRepository = user_repository_interface
        self._role_repo: IRoleRepository = role_repository_interface

    async def _has_super_role(
        self, user: User | CreateUser, roles: list[Role] | None = None
    ) -> bool:
        if hasattr(user, "role_ids") and user.role_ids:
            if not roles:
                roles: dict[UUID, Role] = {
                    role.id: role for role in await self._role_repo.get_all()
                }
            return any(
                roles[role_id].name == settings.SUPER_ROLE_NAME
                for role_id in user.role_ids
            )

        if hasattr(user, "roles") and user.roles:
            return any(role.name == settings.SUPER_ROLE_NAME for role in user.roles)

        return False

    async def _get_not_exist_role_from_user_obj(
        self, user: User | CreateUser, roles: dict[UUID, Role] | None = None
    ) -> UUID | int:
        role_ids = (
            getattr(user, "role_ids", None)
            if getattr(user, "role_ids", None)
            else [role.id for role in getattr(user, "roles", None)]
        )
        if role_ids:
            if not roles:
                roles: dict[UUID, Role] = {
                    role.id: role for role in await self._role_repo.get_all()
                }
            for role_id in role_ids:
                if not roles.get(role_id, None):
                    return role_id

        return 0

    async def get_user_by_id(self, user_id: UUID) -> User:
        try:
            user: User | None = await self._repo.get_by_id(user_id)
            if user is None:
                raise AppExceptions.not_found_exception("User with this id not found")
            if await self._has_super_role(user):
                user.password = None
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

            roles: dict[UUID, Role] = {
                role.id: role for role in await self._role_repo.get_all()
            }
            role_id = await self._get_not_exist_role_from_user_obj(user_info, roles)
            if role_id:
                raise AppExceptions.bad_request_exception(
                    f"Role with id {role_id} not found"
                )
            if await self._has_super_role(user_info, roles):
                raise AppExceptions.forbidden_exception(
                    "Creating a superuser is forbidden"
                )
            return await self._repo.create(user_info)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def update_user(self, user: User, body: CreateUser) -> User:
        try:
            if not (user_info := body.model_dump(exclude_none=True)):
                raise AppExceptions.validation_exception(
                    "At least one parameter must be defined"
                )
            if (
                user_info.get("username", None)
                and user_info["username"] != user.username
                and await self._repo.get_by_username(
                    user_info["username"], exact_match=True, case_sensitive=False
                )
                != []
            ):
                raise AppExceptions.bad_request_exception(
                    f"User with username {user_info['username']} already exists"
                )
            if await self._has_super_role(user):
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
            if await self._has_super_role(user):
                raise AppExceptions.forbidden_exception(
                    "User with super role is not allowed to perform this action"
                )
            return await self._repo.delete(user_id)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def get_user_by_name_or_all(self, username: str) -> list[User]:
        try:
            roles: dict[UUID, Role] = {
                role.id: role for role in await self._role_repo.get_all()
            }
            if username:
                users = await self._repo.get_by_username(username)
                users += await self._repo.get_by_person_name_fields(username)
                unique_users = dict()
                for user in users:
                    if await self._has_super_role(user, roles):
                        user.password = None
                    unique_users[user.id] = user
                return unique_users.values()
            users = await self._repo.get_all()
            for user in users:
                if await self._has_super_role(user, roles):
                    user.password = None
            return users
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def get_user_by_username(self, username: str) -> User:
        try:
            user = await self._repo.get_by_username(
                username, exact_match=True, case_sensitive=True
            )
            if not user:
                raise AppExceptions.not_found_exception("User not found")
            return user[0]
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")
