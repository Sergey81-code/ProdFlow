from abc import ABC, abstractmethod
from uuid import UUID

from api.v1.departments.schemas import CreateDepartment, Department, UpdateDepartment


class IDepartmentRepository(ABC):
    @abstractmethod
    async def get_departments(
        self,
        id: UUID | None = None,
        name: str | None = None,
        code: str | None = None,
    ) -> list[Department]:
        """
        Returns a list of departments filtered by the provided parameters.
        If multiple parameters are provided, they are combined using AND logic.
        If no parameters are provided, returns all departments.
        """
        pass

    @abstractmethod
    async def create(self, department_info: CreateDepartment) -> Department:
        pass

    @abstractmethod
    async def update(
        self, department: Department, new_department_info: UpdateDepartment
    ) -> Department:
        pass

    @abstractmethod
    async def delete(self, department_id: UUID) -> UUID:
        pass
