from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ProdJournalRoute(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rec_id: int | None = None

    user_id: UUID | None = None

    prod_id: str
    opr_num: int | None = None

    journal_id: str | None = None
    voucher: str | None = None
    line_num: int | None = None
    trans_date: date | None = None

    job_type: str | None = None
    wrkctr_id: str | None = None

    hours: Decimal | None = None
    hour_price: Decimal | None = None

    qty_good: Decimal | None = None
    qty_error: Decimal | None = None

    empl_id: str | None = None

    opr_finished: bool | None = None
    job_finished: bool | None = None

    executed_pct: Decimal | None = None

    from_time: time | None = None
    to_time: time | None = None

    opr_id: str | None = None

    cancelled: bool | None = None
    error_cause: str | None = None

    created_date_time: datetime | None = None
    modified_date_time: datetime | None = None
