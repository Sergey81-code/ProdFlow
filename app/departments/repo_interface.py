from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.departments.models import Department


class IDepartmentRepository(ABC):

    @abstractmethod
    async def create(self, department_info: dict[str, Any]) -> Department:
        pass

    @abstractmethod
    async def update(
        self, department: Department, new_department_info: dict[str, Any]
    ) -> Department:
        pass

    @abstractmethod
    async def delete(self, department_id: UUID) -> UUID:
        pass

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
