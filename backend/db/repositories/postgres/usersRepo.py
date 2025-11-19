from uuid import UUID

from sqlalchemy import or_, select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.users.repo_interface import IUserRepository
from api.v1.users.schemas import CreateUser, UpdateUser, User

from db.models import Role, User as UserDb
from db.repositories.postgres.utils import escape_tsquery


class PostgresUserRepo(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session: AsyncSession = session

    async def get_by_id(self, id: UUID) -> User | None:
        stmt = select(UserDb).where(UserDb.id == id)
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        return User.model_validate(user) if user else None

    async def create(self, info: CreateUser) -> User:
        user = UserDb(**info.model_dump(exclude_none=True))
        full_name = f"{user.first_name} {user.last_name} {user.patronymic or ''}"
        user.full_name_tsv = func.to_tsvector("russian", full_name)
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

    async def get_by_username(
        self, name: str, exact_match: bool = False, case_sensitive: bool = False
    ) -> list[User]:
        if exact_match:
            pattern = name
            filter_expr = (
                UserDb.username == pattern
                if case_sensitive
                else func.lower(UserDb.username) == pattern.lower()
            )
        else:
            pattern = f"%{name}%"
            filter_expr = (
                UserDb.username.like(pattern)
                if case_sensitive
                else UserDb.username.ilike(pattern)
            )
        stmt = select(UserDb).where(filter_expr)
        result = await self._session.execute(stmt)
        users = result.scalars().all()
        return [User.model_validate(u) for u in users]

    async def get_by_person_name_fields(self, name: str) -> list[User]:
        """
        Full-text search for users by first name, last name, or patronymic.
        Works with multiple words in any order, partial matches supported.
        """

        words = [escape_tsquery(w.strip()) for w in name.split() if w.strip()]
        query = " & ".join(f"{word}:*" for word in words if word)

        stmt = select(UserDb).where(
            UserDb.full_name_tsv.op("@@")(func.to_tsquery("russian", query))
        )

        result = await self._session.execute(stmt)
        users = result.scalars().all()
        return [User.model_validate(u) for u in users]

    async def get_all(self) -> list[User]:
        stmt = select(UserDb)
        result = await self._session.execute(stmt)
        users = result.scalars().all()
        return [User.model_validate(u) for u in users]

    async def get_user_permissions(self, user_id: UUID) -> list[str]:
        stmt = (
            select(func.unnest(Role.permissions))
            .select_from(UserDb)
            .join(Role, Role.id == func.any(UserDb.role_ids))
            .where(UserDb.id == user_id)
        )
        result = await self._session.execute(stmt)
        return list(set(result.scalars().all()))
