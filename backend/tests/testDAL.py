from typing import Callable
from uuid import UUID
import asyncpg
from sqlalchemy import Enum, Table

from db.models import Base


class TestDAL:
    def __init__(self, asyncpg_pool: asyncpg.Pool):
        self.pool = asyncpg_pool

    async def get_obj_from_database_by_id(
        self, tablename: str, obj_id: UUID
    ) -> asyncpg.Record | None:
        query = f"""
            SELECT * FROM {tablename}
            WHERE id = $1 
        """
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, obj_id)

    async def get_all(
        self, tablename: str, object_filters: list[Callable[[str], str]] | None = None
    ) -> list[asyncpg.Record] | list:
        query = f"""SELECT * FROM {tablename}"""

        if object_filters:
            filters = [filter_func(tablename) for filter_func in object_filters]
            query += " WHERE " + " AND ".join(filters)

        async with self.pool.acquire() as connection:
            result = await connection.fetch(query)
            return [record for record in result]

    @staticmethod
    async def get_sqla_model_by_tablename(tablename: str) -> Table | None:
        for cls in Base.__subclasses__():
            if hasattr(cls, "__tablename__") and cls.__tablename__ == tablename:
                return cls.__table__
        return

    @staticmethod
    async def auto_cast_enum_values(obj: dict, table: Table) -> dict:
        new_obj = obj.copy()
        for column in table.columns:
            if isinstance(column.type, Enum):
                val = new_obj.get(column.name)
                if val is None:
                    continue
                enum_class = column.type.enum_class

                if isinstance(val, enum_class):
                    new_obj[column.name] = val.value.upper()
                elif isinstance(val, str):
                    try:
                        enum_member = enum_class(val)
                        new_obj[column.name] = enum_member.value.upper()
                    except ValueError:
                        raise ValueError(
                            f"Invalid enum value '{val}' for {column.name}"
                        )
                else:
                    pass
        return new_obj

    async def create_object_in_database(
        self, tablename: str, obj: dict, field_to_return: str = "id"
    ) -> str | None:
        table = await self.get_sqla_model_by_tablename(tablename)
        if table is not None:
            obj = await self.auto_cast_enum_values(obj, table)
        columns = '"' + '", "'.join(obj.keys()) + '"'
        value_placeholders = ", ".join([f"${i+1}" for i in range(len(obj))])
        values = tuple(obj.values())
        query = f"""
            INSERT INTO {tablename} ({columns})
            VALUES ({value_placeholders})
            RETURNING {field_to_return}
        """
        async with self.pool.acquire() as connection:
            return await connection.fetchval(query, *values)
