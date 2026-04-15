from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.production_routes.models import ProdRoute
from db.models.production import ProdRoute as ProdRouteDb
from app.production_routes.repo_interface import IProdRouteRepository


class ProdRoutePostgresRepository(IProdRouteRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert_many(self, routes: list[ProdRoute]) -> list[ProdRoute]:
        if not routes:
            return

        stmt = insert(ProdRouteDb).values(
            [
                {
                    "id": r.id,
                    "prod_id": r.prod_id,
                    "opr_num": r.opr_num,
                    "level": r.level,
                    "opr_id": r.opr_id,
                    "wrkctr_id": r.wrkctr_id,
                    "setup_time": r.setup_time,
                    "process_time": r.process_time,
                    "process_per_qty": r.process_per_qty,
                    "transp_time": r.transp_time,
                    "queue_time_before": r.queue_time_before,
                    "queue_time_after": r.queue_time_after,
                    "calc_qty": r.calc_qty,
                    "opr_finished": r.opr_finished,
                    "from_date": r.from_date,
                    "to_date": r.to_date,
                    "from_time": r.from_time,
                    "to_time": r.to_time,
                    "opr_priority": r.opr_priority,
                    "job_id_process": r.job_id_process,
                    "created_date_time": r.created_date_time,
                    "modified_date_time": r.modified_date_time,
                }
                for r in routes
            ]
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[
                ProdRouteDb.prod_id,
                ProdRouteDb.opr_num,
            ],
            set_={
                col.name: getattr(stmt.excluded, col.name)
                for col in ProdRouteDb.__table__.columns
                if col.name
                not in {
                    "ProdId",
                    "OprNum",
                }
            },
        ).returning(ProdRouteDb)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return [
            ProdRoute.model_validate(obj) for obj in result.unique().scalars().all()
        ]

    async def list_by_order(self, prod_id: str) -> list[ProdRoute]:
        result = await self._session.execute(
            select(ProdRouteDb).where(ProdRouteDb.prod_id == prod_id)
        )
        return [
            ProdRoute.model_validate(obj) for obj in result.unique().scalars().all()
        ]

    async def get(self, prod_id: str, opr_num: int) -> ProdRoute | None:
        result = await self._session.execute(
            select(ProdRouteDb).where(
                ProdRouteDb.prod_id == prod_id, ProdRouteDb.opr_num == opr_num
            )
        )

        prod_route = result.scalar_one_or_none()
        if prod_route:
            return ProdRoute.model_validate(prod_route)
        return None
