from abc import ABC, abstractmethod

from app.production_routes.models import ProdRoute


class IProdRouteRepository(ABC):
    @abstractmethod
    async def upsert_many(self, routes: list[ProdRoute]) -> list[ProdRoute]: ...

    @abstractmethod
    async def list_by_order(self, prod_id: str) -> list[ProdRoute]: ...

    @abstractmethod
    async def get(self, prod_id: str, opr_num: int) -> ProdRoute | None: ...
