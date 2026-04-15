from datetime import date, datetime, time
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ProdJournalRouteRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    action: str
    user_id: UUID

    prod_id: str
    journal_id: str
    opr_num: int
    line_num: int | None = None

    record_date: date | None = None
    record_time: time | None = None
    created_date_time: datetime | None = None
