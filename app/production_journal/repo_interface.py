from abc import ABC, abstractmethod

from app.production_journal.models import ProdJournal


class IProdJournalRepository(ABC):
    @abstractmethod
    async def upsert(self, journal: ProdJournal) -> None: ...

    @abstractmethod
    async def list_by_order(self, prod_id: str) -> list[ProdJournal]: ...
