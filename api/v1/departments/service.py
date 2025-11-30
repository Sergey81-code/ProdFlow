from uuid import UUID
from api.core.exceptions import AppExceptions
from api.v1.departments.repo_interface import IDepartmentRepository
from api.v1.departments.schemas import CreateDepartment, Department, UpdateDepartment
from db.db_exceptions import DBException


class DepartmentService:
    def init(self, repo: IDepartmentRepository):
        self._repo: IDepartmentRepository = repo

    async def _is_department_exists(
        self, department: Department | CreateDepartment | UpdateDepartment
    ) -> bool:
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
        return False

    async def create_department_in_database(
        self, department_info: CreateDepartment
    ) -> Department:
        try:
            if self._is_department_exists(department_info):
                raise AppExceptions.bad_request_exception(
                    "Department with provided parameters already exists"
                )
            return await self._repo.create(department_info)

        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def get_departments(
        self, id: UUID | None = None, name: str | None = None, code: str | None = None
    ) -> list[Department]:

        departments = await self._repo.get_departments(id=id, name=name, code=code)

        if not departments:
            raise AppExceptions.not_found_exception("No departments found")

        return departments

    async def update_department(
        self, department: Department, new_department_info: UpdateDepartment
    ) -> Department:
        try:
            new_department_info.name = (
                None
                if new_department_info.name == department.name
                else new_department_info.name
            )
            new_department_info.code = (
                None
                if new_department_info.code == department.code
                else new_department_info.code
            )
            new_department_info = new_department_info.model_dump(exclude_none=True)
            if not new_department_info:
                raise AppExceptions.validation_exception(
                    "At least one parameter must be defined"
                )

            if await self._is_department_exists(new_department_info):
                raise AppExceptions.bad_request_exception(
                    "Department with provided parameters already exists"
                )
            return await self._repo.update(department, new_department_info)
        except DBException:
            raise AppExceptions.service_unavailable_exception("Database error.")

    async def delete_department_by_id(self, department_id: UUID) -> UUID:
        return await self._repo.delete(department_id)
