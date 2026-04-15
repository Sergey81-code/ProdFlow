from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.production_journal.models import ProdJournal
from app.production_journal.repo_interface import IProdJournalRepository
from db.models.production import ProdJournal as ProdJournalDb


class ProdJournalRepository(IProdJournalRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert(self, journal: ProdJournal) -> None:
        stmt = insert(ProdJournalDb).values(
            rec_id=journal.rec_id,
            journal_id=journal.journal_id,
            description=journal.description,
            prod_id=journal.prod_id,
            opr_num=journal.opr_num,
            journal_type=journal.journal_type,
            posted=journal.posted,
            qty_good=journal.qty_good,
            qty_error=journal.qty_error,
            end_job=journal.end_job,
            auto_report_finished=journal.auto_report_finished,
            route_auto_pick_list=journal.route_auto_pick_list,
            prod_auto_pick_list=journal.prod_auto_pick_list,
            created_date_time=journal.created_date_time,
            modified_date_time=journal.modified_date_time,
        )

        update_cols = {
            c.name: getattr(stmt.excluded, c.name)
            for c in ProdJournalDb.__table__.columns
            if c.name not in ("journal_id")
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=[ProdJournalDb.journal_id],
            set_=update_cols,
        )

        await self._session.execute(stmt)
        await self._session.commit()

    async def list_by_order(self, prod_id: str) -> list[ProdJournal]:
        result = await self._session.execute(
            select(ProdJournalDb).where(ProdJournalDb.prod_id == prod_id)
        )
        return [
            ProdJournal.model_validate(obj) for obj in result.unique().scalars().all()
        ]
