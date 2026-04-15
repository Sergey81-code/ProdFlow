from abc import ABC, abstractmethod

from integrations.ERM.dto.aggregates import ProdOrderAggregateDTO


class ERMProdOrderSinkPort(ABC):
    @abstractmethod
    async def send_prod_order(
        self,
        aggregate: ProdOrderAggregateDTO,
    ) -> None: ...
