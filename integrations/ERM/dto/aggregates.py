from dataclasses import dataclass
from integrations.ERM.dto.prod_bom import ProdBOMDTO
from integrations.ERM.dto.prod_journal import ProdJournalDTO
from integrations.ERM.dto.prod_journal_route import ProdJournalRouteDTO
from integrations.ERM.dto.prod_order import ProdOrderDTO
from integrations.ERM.dto.prod_router import ProdRouteDTO


@dataclass(slots=True)
class ProdOrderAggregateDTO:
    order: ProdOrderDTO
    routes: list[ProdRouteDTO]
    journals: list[ProdJournalDTO]
    journal_routes: list[ProdJournalRouteDTO]
