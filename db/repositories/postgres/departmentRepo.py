from typing import Any
from uuid import UUID

from sqlalchemy import and_, delete, select, update
from app.departments.models import Department
from app.departments.repo_interface import IDepartmentRepository
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Department as DepartmentDb


class PostgresDepartmentRepo(IDepartmentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, department_info: dict[str, Any]) -> Department:
        department = DepartmentDb(**department_info)
        self._session.add(department)
        await self._session.commit()
        await self._session.refresh(department)
        return Department.model_validate(department)

    async def update(
        self, department: Department, new_department_info: dict[str, Any]
    ) -> Department:
        stmt = (
            update(DepartmentDb)
            .where(DepartmentDb.id == department.id)
            .values(**new_department_info)
            .returning(DepartmentDb)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        updated_department = result.scalar_one()
        return Department.model_validate(updated_department)

    async def delete(self, id: UUID) -> UUID:
        stmt = (
            delete(DepartmentDb).where(DepartmentDb.id == id).returning(DepartmentDb.id)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        deleted_id = result.scalar_one_or_none()
        return deleted_id

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
        stmt = select(DepartmentDb)
        filters = []

        if id is not None:
            filters.append(DepartmentDb.id == id)

        if name is not None:
            filters.append(DepartmentDb.name.ilike(f"%{name}%"))

        if code is not None:
            filters.append(DepartmentDb.code == code)

        if filters:
            stmt = stmt.where(and_(*filters))

        result = await self._session.execute(stmt)
        items = result.scalars().all()

        return [Department.model_validate(obj) for obj in items]
