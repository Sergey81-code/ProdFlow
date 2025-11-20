from uuid import UUID

from api.core.config import get_settings
from api.core.exceptions import AppExceptions
from api.v1.roles.repo_interface import IRoleRepository
from api.v1.roles.schemas import CreateRole, Role
from db.db_exceptions import DBException

settings = get_settings()


class RoleService:
    def __init__(self, role_repository_interface: IRoleRepository):
        self._repo: IRoleRepository = role_repository_interface

    async def get_role_by_id(self, role_id: UUID) -> Role:
        try:
            role: Role | None = await self._repo.get_by_id(role_id)
            if role is None:
                raise AppExceptions.not_found_exception("Role with this id not found")
            return role
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def create_role_in_database(self, role_info: CreateRole) -> Role:
        try:
            if role_info.name.lower() == settings.SUPER_ROLE_NAME.lower():
                raise AppExceptions.forbidden_exception(
                    "Role with this name is not allowed to create"
                )
            if (
                await self._repo.get_by_name(
                    role_info.name, exact_match=True, case_sensitive=False
                )
                != []
            ):
                raise AppExceptions.bad_request_exception(
                    f"Role with name {role_info.name} already exists."
                )
            return await self._repo.create(role_info)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def update_role(self, role: Role, body: CreateRole) -> Role:
        try:
            if role.name.lower() == settings.SUPER_ROLE_NAME.lower():
                raise AppExceptions.forbidden_exception(
                    "Super role is not allowed to perform this action"
                )

            if (
                body.name
                and body.name != role.name
                and await self._repo.get_by_name(
                    body.name, exact_match=True, case_sensitive=False
                )
                != []
            ):
                raise AppExceptions.bad_request_exception(
                    f"Role with name {body.name} already exists."
                )

            role_info = body.model_dump(exclude_none=True)
            if not role_info:
                raise AppExceptions.validation_exception(
                    "At least one parameter must be defined"
                )
            return await self._repo.update(role, body)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def delete_role_by_id(self, role_id: UUID) -> UUID:
        try:
            role: Role | None = await self._repo.get_by_id(role_id)
            if role is None:
                raise AppExceptions.not_found_exception("Role with this id not found")
            if role.name == settings.SUPER_ROLE_NAME:
                raise AppExceptions.forbidden_exception(
                    "Super role is not allowed to perform this action"
                )
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
