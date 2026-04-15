from typing import Any
from uuid import UUID
from app.core.exceptions.api_exceptions import ApiExceptions
from app.core.exceptions.db_exceptions import DbExceptions
from app.departments.models import Department
from app.departments.repo_interface import IDepartmentRepository


class DepartmentService:
    def __init__(self, repo: IDepartmentRepository):
        self._repo: IDepartmentRepository = repo

    async def _is_department_exists(
        self, department: Department | dict[str, Any]
    ) -> bool:
        if isinstance(department, Department):
            if (
                department.name
                and await self._repo.get_departments(name=department.name) != []
            ):
                return True
            if (
                department.code
                and await self._repo.get_departments(code=department.code) != []
            ):
                return True
        elif isinstance(department, dict):
            if (
                department.get("name")
                and await self._repo.get_departments(name=department["name"]) != []
            ):
                return True
            if (
                department.get("code")
                and await self._repo.get_departments(code=department["code"]) != []
            ):
                return True
        return False

    async def create_department_in_database(
        self, department_info: dict[str, Any]
    ) -> Department:
        try:
            if await self._is_department_exists(department_info):
                raise ApiExceptions.bad_request_exception(
                    "Department with provided parameters already exists"
                )
            return await self._repo.create(department_info)

        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def get_departments(
        self, id: UUID | None = None, name: str | None = None, code: str | None = None
    ) -> list[Department]:

        departments = await self._repo.get_departments(id=id, name=name, code=code)

        if not departments:
            raise ApiExceptions.not_found_exception("No departments found")

        return departments

    async def update_department(
        self, department: Department, new_department_info: dict[str, Any]
    ) -> Department:
        try:
            if new_department_info.get("name") == department.name:
                new_department_info.pop("name")

            if new_department_info.get("code") == department.code:
                new_department_info.pop("code")

            if not new_department_info:
                raise ApiExceptions.validation_exception(
                    "At least one parameter must be defined"
                )

            if await self._is_department_exists(new_department_info):
                raise ApiExceptions.bad_request_exception(
                    "Department with provided parameters already exists"
                )
            return await self._repo.update(department, new_department_info)
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def delete_department_by_id(self, department_id: UUID) -> UUID:
        try:
            departments: Department | None = await self._repo.get_departments(
                id=department_id
            )
            if departments == []:
                raise ApiExceptions.not_found_exception(
                    "Department with this id not found"
                )
            return await self._repo.delete(department_id)
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")
