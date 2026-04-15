from typing import Any

from sqlalchemy import select, update

from app.production_journal_route_records.models import ProdJournalRouteRecord
from app.production_journal_route_records.repo_interface import (
    IProdJournalRouteRecordRepository,
)
from db.models.production import ProdJournalRouteRecords as ProdJournalRouteRecordDb
from sqlalchemy.ext.asyncio import AsyncSession

from utils.make_naive import MakeNaive


class ProdJournalRouteRecordRepository(IProdJournalRouteRecordRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(
        self,
        prod_id: str,
        journal_id: str,
        opr_num: int,
        line_num: int,
    ) -> list[ProdJournalRouteRecord]:
        result = await self._session.execute(
            select(ProdJournalRouteRecordDb).where(
                ProdJournalRouteRecordDb.prod_id == prod_id,
                ProdJournalRouteRecordDb.journal_id == journal_id,
                ProdJournalRouteRecordDb.opr_num == opr_num,
                ProdJournalRouteRecordDb.line_num == line_num,
            )
        )

        return [
            ProdJournalRouteRecord.model_validate(obj) for obj in result.scalars().all()
        ]

    async def get_by_id(self, id: int) -> ProdJournalRouteRecord | None:
        result = await self._session.execute(
            select(ProdJournalRouteRecordDb).where(
                ProdJournalRouteRecordDb.id == id,
            )
        )

        prod_journal_route_record_from_db = result.scalar_one_or_none()
        if prod_journal_route_record_from_db:
            return ProdJournalRouteRecord.model_validate(
                prod_journal_route_record_from_db
            )
        return None

    async def create(
        self, journal_route_record: ProdJournalRouteRecord
    ) -> ProdJournalRouteRecord:
        journal_route_record = await MakeNaive.make_naive_obj(journal_route_record)
        prod_journal_route_record = ProdJournalRouteRecordDb(
            **(journal_route_record.model_dump())
        )
        self._session.add(prod_journal_route_record)
        await self._session.commit()
        await self._session.refresh(prod_journal_route_record)
        return ProdJournalRouteRecord.model_validate(prod_journal_route_record)

    async def update(
        self, journal_route_record: ProdJournalRouteRecord, update_data: dict[str, Any]
    ) -> ProdJournalRouteRecord:
        update_data = await MakeNaive.make_naive_dict(update_data)
        stmt = (
            update(ProdJournalRouteRecordDb)
            .where(ProdJournalRouteRecordDb.id == journal_route_record.id)
            .values(**update_data)
            .returning(ProdJournalRouteRecordDb)
        )

        result = await self._session.execute(stmt)
        await self._session.commit()
        return ProdJournalRouteRecord.model_validate(result.scalar_one_or_none())
