from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.roles.repo_interface import IRoleRepository
from api.v1.roles.schemas import CreateRole, Role, UpdateRole
from db.models import Role as RoleDb


class PostgresRoleRepo(IRoleRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: UUID) -> Role | None:
        stmt = select(RoleDb).where(RoleDb.id == id)
        result = await self._session.execute(stmt)
        role = result.scalar_one_or_none()
        return Role.model_validate(role) if role else None

    async def create(self, info: CreateRole) -> Role:
        role = RoleDb(**info.model_dump(exclude_none=True))
        self._session.add(role)
        await self._session.commit()
        await self._session.refresh(role)
        return Role.model_validate(role)

    async def update(self, role: Role, info: UpdateRole) -> Role:
        stmt = (
            update(RoleDb)
            .where(RoleDb.id == role.id)
            .values(**info.model_dump(exclude_none=True))
            .returning(RoleDb)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        updated_role = result.scalar_one()
        return Role.model_validate(updated_role)

    async def delete(self, id: UUID) -> UUID:
        stmt = delete(RoleDb).where(RoleDb.id == id).returning(RoleDb.id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        deleted_id = result.scalar_one_or_none()
        return deleted_id

    async def get_by_name(
        self, name: str, exact_match: bool = False, case_sensitive: bool = False
    ) -> list[Role]:
        if exact_match:
            pattern = name
            filter_expr = (
                RoleDb.name == pattern
                if case_sensitive
                else func.lower(RoleDb.name) == pattern.lower()
            )
        else:
            pattern = f"%{name}%"
            filter_expr = (
                RoleDb.name.like(pattern)
                if case_sensitive
                else RoleDb.name.ilike(pattern)
            )

        stmt = select(RoleDb).where(filter_expr)
        result = await self._session.execute(stmt)
        roles = result.scalars().all()
        return [Role.model_validate(r) for r in roles]

    async def get_all(self) -> list[Role]:
        stmt = select(RoleDb)
        result = await self._session.execute(stmt)
        roles = result.scalars().all()
        return [Role.model_validate(r) for r in roles]
