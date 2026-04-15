from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from integrations.ERM.dto.aggregates import ProdOrderAggregateDTO


class ERMProdOrderSourcePort(ABC):
    @abstractmethod
    async def load_prod_orders(
        self,
        modified_since: str | None = None,
        prod_ids: list[str] | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[ProdOrderAggregateDTO]: ...
