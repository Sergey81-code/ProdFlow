from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.production_journal.models import ProdJournal
from app.production_journal_routes.models import ProdJournalRoute
from app.production_orders.models import ProdOrder
from app.production_routes.models import ProdRoute


class TunedModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProdOrderAggregateSchema(TunedModel):
    order: ProdOrder
    routes: list[ProdRoute]
    journals: list[ProdJournal]
    journal_routes: list[ProdJournalRoute]


class UpdateProdOrderStatus(TunedModel):
    prod_status: int | None = None
    prod_locked: bool | None = None
    sched_status: str | None = None
    prod_prio: int | None = None
    remark: str | None = None


class CreateProdJournalRoute(TunedModel):
    opr_num: int = Field(..., ge=0)
    line_num: int = Field(default=1, ge=1)

    opr_finished: bool = Field(default=False)
    job_finished: bool = Field(default=False)

    trans_date: date | None = None
    job_type: str | None = None
    wrkctr_id: str | None = None

    hours: Decimal | None = None
    hour_price: Decimal | None = None

    qty_good: Decimal | None = None
    qty_error: Decimal | None = None

    empl_id: str | None = None

    from_time: time | None = None
    to_time: time | None = None

    cancelled: bool = Field(default=False)

    error_cause: str | None = None


class UpdateProdJournalRoute(TunedModel):
    trans_date: date | None = None
    job_type: str | None = None
    wrkctr_id: str | None = None

    hours: Decimal | None = None
    hour_price: Decimal | None = None

    qty_good: Decimal | None = None
    qty_error: Decimal | None = None

    empl_id: str | None = None

    from_time: time | None = None
    to_time: time | None = None

    opr_finished: bool | None = None
    job_finished: bool | None = None

    cancelled: bool | None = None
    error_cause: str | None = None


class UpdateProdJournalRouteRecord(TunedModel):
    action: str | None = None
    user_id: UUID | None = None

    prod_id: str | None = None
    journal_id: str | None = None
    opr_num: int | None = None
    line_num: int | None = None

    record_date: date | None = None
    record_time: time | None = None
    created_date_time: datetime | None = None


class ProdJournalRouteRecordResponse(BaseModel):
    action: str
    user_id: UUID
    username: str

    prod_id: str
    journal_id: str
    opr_num: int
    line_num: int

    record_date: date
    record_time: time
    created_date_time: datetime
