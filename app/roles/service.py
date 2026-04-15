from typing import Any
from uuid import UUID

from api.core.config import get_settings
from app.core.exceptions.api_exceptions import ApiExceptions
from app.core.exceptions.db_exceptions import DbExceptions
from app.roles.models import Role
from app.roles.repo_interface import IRoleRepository
from app.core.exceptions.db_exceptions import DbExceptions

settings = get_settings()


class RoleService:
    def __init__(self, role_repository_interface: IRoleRepository):
        self._repo: IRoleRepository = role_repository_interface

    async def get_role_by_id(self, role_id: UUID) -> Role:
        try:
            role: Role | None = await self._repo.get_by_id(role_id)
            if role is None:
                raise ApiExceptions.not_found_exception("Role with this id not found")
            return role
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def create_role_in_database(self, role_info: dict[str, Any]) -> Role:
        try:
            if role_info["name"].lower() == settings.SUPER_ROLE_NAME.lower():
                raise ApiExceptions.forbidden_exception(
                    "Role with this name is not allowed to create"
                )
            if (
                await self._repo.get_by_name(
                    role_info["name"], exact_match=True, case_sensitive=False
                )
                != []
            ):
                raise ApiExceptions.bad_request_exception(
                    f"Role with name {role_info["name"]} already exists."
                )
            return await self._repo.create(role_info)
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def update_role(self, role: Role, role_info: dict[str, Any]) -> Role:
        try:
            if role.name.lower() == settings.SUPER_ROLE_NAME.lower():
                raise ApiExceptions.forbidden_exception(
                    "Super role is not allowed to perform this action"
                )

            if not role_info:
                raise ApiExceptions.validation_exception(
                    "At least one parameter must be defined"
                )

            if (
                role_info.get("name")
                and role_info["name"] != role.name
                and await self._repo.get_by_name(
                    role_info["name"], exact_match=True, case_sensitive=False
                )
                != []
            ):
                raise ApiExceptions.bad_request_exception(
                    f"Role with name {role_info["name"]} already exists."
                )

            return await self._repo.update(role, role_info)
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def delete_role_by_id(self, role_id: UUID) -> UUID:
        try:
            role: Role | None = await self._repo.get_by_id(role_id)
            if role is None:
                raise ApiExceptions.not_found_exception("Role with this id not found")
            if role.name == settings.SUPER_ROLE_NAME:
                raise ApiExceptions.forbidden_exception(
                    "Super role is not allowed to perform this action"
                )
            return await self._repo.delete(role_id)
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def get_role_by_name_or_all(self, role_name: str) -> list[Role]:
        try:
            if role_name:
                return await self._repo.get_by_name(role_name)
            return await self._repo.get_all()
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")
