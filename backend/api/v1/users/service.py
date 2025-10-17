from uuid import UUID
from api.core.exceptions import AppExceptions
from api.v1.users.schemas import CreateUser, User
from api.v1.users.repo_interface import UserRepoInterface
from db.db_exceptions import DBException


class UserService:
    def __init__(self, user_repository_interface: UserRepoInterface):
        self._repo: UserRepoInterface = user_repository_interface

    async def get_user_by_id(self, user_id: UUID) -> User:
        try:
            return await self._repo.get_by_id(user_id)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def create_user_in_database(self, user_info: CreateUser) -> User:
        try:
            return await self._repo.create(user_info)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def update_user(self, user: User, body: CreateUser) -> User:
        try:
            return await self._repo.update(user, body)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def delete_user_by_id(self, user_id: UUID) -> UUID:
        try:
            return await self._repo.delete(user_id)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def get_user_by_name_or_all(self, user_name: str) -> list[User]:
        try:
            if user_name:
                return await self._repo.get_by_name(user_name)
            return await self._repo.get_all()
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")
