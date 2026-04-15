from dataclasses import asdict
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional
from app.production_journal.models import ProdJournal

from app.production_journal_route_records.models import ProdJournalRouteRecord
from app.production_journal_routes.models import ProdJournalRoute
from app.production_orders.models import ProdOrder
from app.production_routes.models import ProdRoute
from config.actions import Actions
from integrations.ERM.dto.aggregates import ProdOrderAggregateDTO


if TYPE_CHECKING:
    from integrations.ERM.ports.sink import ERMProdOrderSinkPort
    from integrations.ERM.ports.source import ERMProdOrderSourcePort
    from app.production_routes.repo_interface import IProdRouteRepository
    from app.users.repo_interface import IUserRepository
    from app.production_orders.repo_interface import IProdOrderRepository
    from app.production_journal_routes.repo_interface import IProdJournalRouteRepository
    from app.production_journal.repo_interface import IProdJournalRepository
    from app.production_journal_route_records.repo_interface import (
        IProdJournalRouteRecordRepository,
    )


class ERMProdOrderLoadService:
    def __init__(
        self,
        erm_source_port: Optional["ERMProdOrderSourcePort"] = None,
        erm_sink_port: Optional["ERMProdOrderSinkPort"] = None,
        order_repo: Optional["IProdOrderRepository"] = None,
        route_repo: Optional["IProdRouteRepository"] = None,
        journal_repo: Optional["IProdJournalRepository"] = None,
        journal_route_repo: Optional["IProdJournalRouteRepository"] = None,
        user_repo: Optional["IUserRepository"] = None,
        journal_route_record_repo: Optional["IProdJournalRouteRecordRepository"] = None,
    ):
        self._erm_source_port: "ERMProdOrderSourcePort" = erm_source_port
        self._erm_sink_port: "ERMProdOrderSinkPort" = erm_sink_port
        self._order_repo: "IProdOrderRepository" = order_repo
        self._route_repo: "IProdRouteRepository" = route_repo
        self._journal_repo: "IProdJournalRepository" = journal_repo
        self._journal_route_repo: "IProdJournalRouteRepository" = journal_route_repo
        self._user_repo: "IUserRepository" = user_repo
        self._journal_route_record_repo: "IProdJournalRouteRecordRepository" = (
            journal_route_record_repo
        )

    async def get_prod_orders(
        self,
        modified_since: str | None = None,
        prod_ids: list[str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []

        async for raw_aggregate in self._erm_source_port.load_prod_orders(
            modified_since=modified_since, prod_ids=prod_ids, limit=limit
        ):
            order = ProdOrder(**asdict(raw_aggregate.order))

            routes = [ProdRoute(**asdict(r)) for r in raw_aggregate.routes]

            journals = [ProdJournal(**asdict(j)) for j in raw_aggregate.journals]

            journal_routes = [
                ProdJournalRoute(**asdict(jr)) for jr in raw_aggregate.journal_routes
            ]

            result.append(
                {
                    "order": order,
                    "routes": routes,
                    "journals": journals,
                    "journal_routes": journal_routes,
                }
            )

        return result

    async def load_prod_orders_to_db(
        self,
        modified_since: str | None = None,
        prod_ids: list[str] | None = None,
        limit: int | None = None,
    ) -> None:
        async for aggregate in self._erm_source_port.load_prod_orders(
            modified_since=modified_since, prod_ids=prod_ids, limit=limit
        ):
            await self._process_order_aggregate(aggregate)

    async def _process_order_aggregate(self, aggregate: ProdOrderAggregateDTO):
        order = ProdOrder(**asdict(aggregate.order))
        await self._order_repo.upsert(order)

        routes = []
        for route_dto in aggregate.routes:
            routes.append(ProdRoute(**asdict(route_dto)))
        await self._route_repo.upsert_many(routes)

        for journal_dto in aggregate.journals:
            journal = ProdJournal(**asdict(journal_dto))
            await self._journal_repo.upsert(journal)

        journal_routes = []
        journal_route_records = []
        for journal_route_dto in aggregate.journal_routes:
            random_user = (await self._user_repo.get_all())[0]
            if not random_user:
                raise RuntimeError("No users found")
            journal_routes.append(
                ProdJournalRoute(
                    user_id=random_user.id,
                    **asdict(journal_route_dto),
                )
            )
            journal_route_record = ProdJournalRouteRecord(
                action=Actions.CREATION,
                user_id=random_user.id,
                prod_id=journal_route_dto.prod_id,
                journal_id=journal_route_dto.journal_id,
                opr_num=journal_route_dto.opr_num,
                line_num=journal_route_dto.opr_num,
                record_date=datetime.now().date(),
                record_time=datetime.now().time(),
                created_date_time=datetime.now(),
            )
            journal_route_records.append(journal_route_record)
        await self._journal_route_repo.upsert(journal_routes)
        for journal_route_record in journal_route_records:
            await self._journal_route_record_repo.create(journal_route_record)
