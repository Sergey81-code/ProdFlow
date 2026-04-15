from abc import ABC, abstractmethod
from typing import Any

from app.production_journal_route_records.models import ProdJournalRouteRecord


class IProdJournalRouteRecordRepository(ABC):
    @abstractmethod
    async def get(
        self,
        prod_id: str,
        journal_id: str,
        opr_num: int,
        line_num: int,
    ) -> list[ProdJournalRouteRecord]: ...

    @abstractmethod
    async def get_by_id(self, id: int) -> ProdJournalRouteRecord | None: ...

    @abstractmethod
    async def create(
        self, journal_route_record: ProdJournalRouteRecord
    ) -> ProdJournalRouteRecord: ...

    @abstractmethod
    async def update(
        self, journal_route_record: ProdJournalRouteRecord, update_data: dict[str, Any]
    ) -> ProdJournalRouteRecord: ...
