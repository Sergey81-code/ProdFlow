from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from .base import BaseDTO


@dataclass(slots=True)
class InventDTO:
    item_id: str

    item_name: str | None = None
    item_group_id: str | None = None
    item_type: str | None = None
    primary_vendor_id: str | None = None

    net_weight: Decimal | None = None
    unit_volume: Decimal | None = None
    bom_unit_id: str | None = None
    minimum_pallet_quantity: int | None = None

    created_date_time: datetime | None = None
    modified_date_time: datetime | None = None
