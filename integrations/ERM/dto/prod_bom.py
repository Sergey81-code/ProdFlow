from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from .base import BaseDTO


@dataclass(slots=True)
class ProdBOMDTO:
    prod_id: str
    line_num: int

    item_id: str | None = None
    bom_qty: Decimal | None = None
    opr_num: int | None = None
    unit_id: str | None = None
    invent_trans_id: str | None = None
    raw_material_date: date | None = None

    created_date_time: datetime | None = None
    modified_date_time: datetime | None = None
