from datetime import date, datetime, time
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class ProdOrder(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int

    prod_id: str

    item_id: str | None = None
    name: str | None = None
    prod_group_id: str | None = None

    prod_status: int | None = None
    prod_prio: int | None = None
    prod_locked: bool | None = None
    prod_type: str | None = None

    sched_status: str | None = None
    sched_date: date | None = None
    sched_start: datetime | None = None
    sched_end: datetime | None = None
    sched_from_time: time | None = None
    sched_to_time: time | None = None

    qty_sched: Decimal | None = None
    qty_st_up: Decimal | None = None

    finished_date: date | None = None
    st_up_date: date | None = None
    dlv_date: date | None = None

    prod_pool_id: str | None = None
    bom_id: str | None = None
    route_id: str | None = None

    invent_location_id: str | None = None
    invent_batch_id: str | None = None
    invent_serial_id: str | None = None

    remark: str | None = None

    created_date_time: datetime | None = None
    modified_date_time: datetime | None = None
