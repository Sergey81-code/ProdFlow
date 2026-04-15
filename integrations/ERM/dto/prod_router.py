from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from .base import BaseDTO


@dataclass(slots=True)
class ProdRouteDTO:
    id: int
    prod_id: str
    opr_num: int

    level: int | None = None
    opr_id: str | None = None
    wrkctr_id: str | None = None

    setup_time: Decimal | None = None
    process_time: Decimal | None = None
    process_per_qty: Decimal | None = None
    transp_time: Decimal | None = None
    queue_time_before: Decimal | None = None
    queue_time_after: Decimal | None = None
    calc_qty: Decimal | None = None

    opr_finished: bool | None = None

    from_date: date | None = None
    to_date: date | None = None
    from_time: time | None = None
    to_time: time | None = None

    opr_priority: int | None = None
    job_id_process: str | None = None

    created_date_time: datetime | None = None
    modified_date_time: datetime | None = None
