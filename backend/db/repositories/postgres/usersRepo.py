from typing import List
from uuid import UUID

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.users.repo_interface import UserRepoInterface
from api.v1.users.schemas import CreateUser, UpdateUser, User

from db.models import Role, User as UserDb


class PostgresUserRepo(UserRepoInterface):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: UUID) -> User | None:
        stmt = select(UserDb).where(UserDb.id == id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        return User.model_validate(user) if user else None

    async def create(self, info: CreateUser) -> User:
        user = UserDb(**info.model_dump(exclude_none=True))
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return User.model_validate(user)

    async def update(self, user: User, info: UpdateUser) -> User:
        stmt = (
            update(UserDb)
            .where(UserDb.id == user.id)
            .values(**info.model_dump(exclude_none=True))
            .returning(UserDb)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        updated_user = result.scalar_one()
        return User.model_validate(updated_user)

    async def delete(self, id: UUID) -> UUID:
        stmt = delete(UserDb).where(UserDb.id == id).returning(UserDb.id)
        result = await self._session.execute(stmt)
        await self._session.commit()
        deleted_id = result.scalar_one_or_none()
        return deleted_id

    async def get_by_name(self, name: str) -> List[User]:
        stmt = select(UserDb).where(UserDb.username.ilike(f"%{name}%"))
        result = await self._session.execute(stmt)
        users = result.scalars().all()
        return [User.model_validate(u) for u in users]

    async def get_all(self) -> List[User]:
        stmt = select(UserDb)
        result = await self._session.execute(stmt)
        users = result.scalars().all()
        return [User.model_validate(u) for u in users]


async def get_user_permissions(self, user_id: UUID) -> list[str]:
    stmt = (
        select(func.unnest(Role.permissions))
        .join(Role, Role.id == func.any(User.role_ids))
        .where(User.id == user_id)
    )

    result = await self._session.execute(stmt)
    permissions = result.scalars().all()
    return list(set(permissions))
