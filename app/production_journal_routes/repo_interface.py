from abc import ABC, abstractmethod

from app.production_journal_routes.models import ProdJournalRoute


class IProdJournalRouteRepository(ABC):
    @abstractmethod
    async def upsert(
        self, journal_routes: list[ProdJournalRoute]
    ) -> list[ProdJournalRoute]: ...

    @abstractmethod
    async def list_by_order(self, prod_id: str) -> list[ProdJournalRoute]: ...

    @abstractmethod
    async def get(
        self, prod_id: str, journal_id: str, opr_num: int, line_num: int
    ) -> ProdJournalRoute | None: ...
