from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class BaseDTO:
    created_date_time: datetime | None = None
    modified_date_time: datetime | None = None
