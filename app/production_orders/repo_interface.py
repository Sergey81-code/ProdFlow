from abc import ABC, abstractmethod
from typing import Any

from app.production_orders.models import ProdOrder


class IProdOrderRepository(ABC):
    @abstractmethod
    async def upsert(self, order: ProdOrder) -> None: ...

    @abstractmethod
    async def get_by_id(self, prod_id: str) -> ProdOrder | None: ...

    @abstractmethod
    async def list_all(
        self,
        modified_since: str | None = None,
        prod_ids: list[str] | None = None,
        limit: int | None = None,
    ) -> list[ProdOrder]: ...

    @abstractmethod
    async def update_order(
        self, prod_id: str, update_data: dict[str, Any]
    ) -> ProdOrder: ...
