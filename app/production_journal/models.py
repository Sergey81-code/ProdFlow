from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProdJournal(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rec_id: int
    journal_id: str | None = None
    description: str | None = None
    prod_id: str | None = None
    opr_num: int | None = None
    journal_type: str | None = None
    posted: bool | None = None
    qty_good: int | None = None
    qty_error: int | None = None
    end_job: bool | None = None
    auto_report_finished: bool | None = None
    route_auto_pick_list: bool | None = None
    prod_auto_pick_list: bool | None = None

    created_date_time: datetime | None = None
    modified_date_time: datetime | None = None
