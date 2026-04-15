from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select
from sqlalchemy.dialects.postgresql import insert
from app.production_journal_routes.models import ProdJournalRoute
from db.models.production import ProdJournalRoute as ProdJournalRouteDb
from app.production_journal_routes.repo_interface import IProdJournalRouteRepository


class ProdJournalRouteRepository(IProdJournalRouteRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert(
        self, journal_routes: list[ProdJournalRoute]
    ) -> list[ProdJournalRoute]:
        if not journal_routes:
            return []

        values = []

        for jr in journal_routes:
            row = {
                self._get_real_col_name(ProdJournalRouteDb.prod_id): jr.prod_id,
                self._get_real_col_name(ProdJournalRouteDb.opr_num): jr.opr_num,
                self._get_real_col_name(ProdJournalRouteDb.journal_id): jr.journal_id,
                self._get_real_col_name(ProdJournalRouteDb.voucher): jr.voucher,
                self._get_real_col_name(ProdJournalRouteDb.line_num): jr.line_num,
                self._get_real_col_name(ProdJournalRouteDb.trans_date): jr.trans_date,
                self._get_real_col_name(ProdJournalRouteDb.job_type): jr.job_type,
                self._get_real_col_name(ProdJournalRouteDb.wrkctr_id): jr.wrkctr_id,
                self._get_real_col_name(ProdJournalRouteDb.hours): jr.hours,
                self._get_real_col_name(ProdJournalRouteDb.hour_price): jr.hour_price,
                self._get_real_col_name(ProdJournalRouteDb.qty_good): jr.qty_good,
                self._get_real_col_name(ProdJournalRouteDb.qty_error): jr.qty_error,
                self._get_real_col_name(ProdJournalRouteDb.empl_id): jr.empl_id,
                self._get_real_col_name(
                    ProdJournalRouteDb.opr_finished
                ): jr.opr_finished,
                self._get_real_col_name(
                    ProdJournalRouteDb.job_finished
                ): jr.job_finished,
                self._get_real_col_name(
                    ProdJournalRouteDb.executed_pct
                ): jr.executed_pct,
                self._get_real_col_name(ProdJournalRouteDb.from_time): jr.from_time,
                self._get_real_col_name(ProdJournalRouteDb.to_time): jr.to_time,
                self._get_real_col_name(ProdJournalRouteDb.opr_id): jr.opr_id,
                self._get_real_col_name(ProdJournalRouteDb.cancelled): jr.cancelled,
                self._get_real_col_name(ProdJournalRouteDb.error_cause): jr.error_cause,
                self._get_real_col_name(
                    ProdJournalRouteDb.created_date_time
                ): jr.created_date_time,
                self._get_real_col_name(
                    ProdJournalRouteDb.modified_date_time
                ): jr.modified_date_time,
            }

            if jr.rec_id is not None:
                row[self._get_real_col_name(ProdJournalRouteDb.rec_id)] = jr.rec_id

            if jr.user_id is not None:
                row[self._get_real_col_name(ProdJournalRouteDb.user_id)] = jr.user_id

            values.append(row)

        stmt = insert(ProdJournalRouteDb).values(values)

        excluded_cols = {
            col.name: getattr(stmt.excluded, col.name)
            for col in ProdJournalRouteDb.__table__.columns
            if col.name not in {"RecId", "ProdId", "JournalId", "OprNum", "LineNum"}
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=[
                ProdJournalRouteDb.prod_id,
                ProdJournalRouteDb.opr_num,
                ProdJournalRouteDb.journal_id,
                ProdJournalRouteDb.line_num,
            ],
            set_=excluded_cols,
        ).returning(ProdJournalRouteDb)

        result = await self._session.execute(stmt)
        await self._session.commit()
        return [
            ProdJournalRoute.model_validate(obj)
            for obj in result.unique().scalars().all()
        ]

    async def list_by_order(self, prod_id: str) -> list[ProdJournalRoute]:
        result = await self._session.execute(
            select(ProdJournalRouteDb).where(ProdJournalRouteDb.prod_id == prod_id)
        )
        return [
            ProdJournalRoute.model_validate(obj)
            for obj in result.unique().scalars().all()
        ]

    async def get(
        self, prod_id: str, journal_id: str, opr_num: int, line_num: int
    ) -> ProdJournalRoute | None:
        result = await self._session.execute(
            select(ProdJournalRouteDb).where(
                ProdJournalRouteDb.prod_id == prod_id,
                ProdJournalRouteDb.journal_id == journal_id,
                ProdJournalRouteDb.opr_num == opr_num,
                ProdJournalRouteDb.line_num == line_num,
            )
        )

        prod_journal_route_from_db = result.scalar_one_or_none()
        if prod_journal_route_from_db:
            return ProdJournalRoute.model_validate(prod_journal_route_from_db)
        return None

    @staticmethod
    def _get_real_col_name(attr):
        return attr.property.columns[0]
