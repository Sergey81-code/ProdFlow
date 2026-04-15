from datetime import datetime, time, timezone
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from app.production_orders.models import ProdOrder
from db.models.production import ProdOrder as ProdOrderDb
from app.production_orders.repo_interface import IProdOrderRepository
from utils.make_naive import MakeNaive


class ProdOrderRepository(IProdOrderRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def upsert(self, order: ProdOrder) -> None:
        order = MakeNaive.make_naive_obj(order)
        stmt = insert(ProdOrderDb).values(
            id=order.id,
            prod_id=order.prod_id,
            item_id=order.item_id,
            name=order.name,
            prod_group_id=order.prod_group_id,
            prod_status=order.prod_status,
            prod_prio=order.prod_prio,
            prod_locked=order.prod_locked,
            prod_type=order.prod_type,
            sched_status=order.sched_status,
            sched_date=order.sched_date,
            sched_start=order.sched_start,
            sched_end=order.sched_end,
            sched_from_time=order.sched_from_time,
            sched_to_time=order.sched_to_time,
            qty_sched=order.qty_sched,
            qty_st_up=order.qty_st_up,
            finished_date=order.finished_date,
            st_up_date=order.st_up_date,
            dlv_date=order.dlv_date,
            prod_pool_id=order.prod_pool_id,
            bom_id=order.bom_id,
            route_id=order.route_id,
            invent_location_id=order.invent_location_id,
            invent_batch_id=order.invent_batch_id,
            invent_serial_id=order.invent_serial_id,
            remark=order.remark,
            created_date_time=order.created_date_time,
            modified_date_time=order.modified_date_time,
        )

        update_cols = {
            c.name: getattr(stmt.excluded, c.name)
            for c in ProdOrderDb.__table__.columns
            if c.name not in ("id", "prod_id")
        }

        stmt = stmt.on_conflict_do_update(
            index_elements=[ProdOrderDb.prod_id],
            set_=update_cols,
        )

        await self._session.execute(stmt)
        await self._session.commit()

    async def get_by_id(self, prod_id: str) -> ProdOrder | None:
        result = await self._session.execute(
            select(ProdOrderDb).where(ProdOrderDb.prod_id == prod_id)
        )
        result = result.scalar_one_or_none()
        return ProdOrder.model_validate(result) if result else None

    async def list_all(
        self,
        modified_since: str | None = None,
        prod_ids: list[str] | None = None,
        limit: int | None = None,
    ) -> list[ProdOrder]:
        stmt = select(ProdOrderDb)

        if modified_since:
            since_dt = datetime.fromisoformat(modified_since)
            stmt = stmt.where(ProdOrderDb.modified_date_time > since_dt)

        if prod_ids:
            stmt = stmt.where(ProdOrderDb.prod_id.in_(prod_ids))

        if limit is not None:
            stmt = stmt.limit(limit)

        result = await self._session.execute(stmt)
        return [ProdOrder.model_validate(obj) for obj in result.scalars().all()]

    async def update_order(
        self, prod_id: str, update_data: dict[str, Any]
    ) -> ProdOrder:
        stmt = (
            update(ProdOrderDb)
            .where(ProdOrderDb.prod_id == prod_id)
            .values(**update_data)
            .returning(ProdOrderDb)
        )

        result = await self._session.execute(stmt)
        return ProdOrder.model_validate(result.scalar_one_or_none())
