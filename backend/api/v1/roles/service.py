from uuid import UUID
from api.core.exceptions import AppExceptions
from api.v1.roles.repo_interface import RoleRepoInterface
from api.v1.roles.schemas import CreateRole, Role
from db.db_exceptions import DBException


class RoleService:
    def __init__(self, role_repository_interface: RoleRepoInterface):
        self._repo: RoleRepoInterface = role_repository_interface

    async def get_role_by_id(self, role_id: UUID) -> Role:
        try:
            return await self._repo.get_by_id(role_id)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def create_role_in_database(self, role_info: CreateRole) -> Role:
        try:
            return await self._repo.create(role_info)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def update_role(self, role: Role, body: CreateRole) -> Role:
        try:
            return await self._repo.update(role, body)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def delete_role_by_id(self, role_id: UUID) -> UUID:
        try:
            return await self._repo.delete(role_id)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def get_role_by_name_or_all(self, role_name: str) -> list[Role]:
        try:
            if role_name:
                return await self._repo.get_by_name(role_name)
            return await self._repo.get_all()
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")
