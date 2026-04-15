import json
from pathlib import Path
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

from integrations.ERM.dto.aggregates import ProdOrderAggregateDTO
from integrations.ERM.dto.prod_journal import ProdJournalDTO
from integrations.ERM.dto.prod_order import ProdOrderDTO
from integrations.ERM.dto.prod_router import ProdRouteDTO
from integrations.ERM.dto.prod_journal_route import ProdJournalRouteDTO
from integrations.ERM.dto.prod_bom import ProdBOMDTO
from integrations.ERM.ports.source import ERMProdOrderSourcePort


class MockSourceClient(ERMProdOrderSourcePort):
    def __init__(self, json_path: str | Path) -> None:
        self._json_path = Path(json_path)

    async def load_prod_orders(
        self,
        modified_since: str | None = None,
        prod_ids: list[str] | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[ProdOrderAggregateDTO]:

        data = self._load_json()
        aggregates = self._parse_aggregates(data)

        aggregates = self._filter(
            aggregates,
            modified_since=modified_since,
            prod_ids=prod_ids,
            limit=limit,
        )

        for aggregate in aggregates:
            yield aggregate

    def _load_json(self) -> list[dict[str, Any]]:
        with self._json_path.open(encoding="utf-8") as f:
            return json.load(f)

    def _parse_aggregates(
        self,
        raw: dict[str, list[dict[str, Any]]],
    ) -> list[ProdOrderAggregateDTO]:
        aggregates: list[ProdOrderAggregateDTO] = []

        for item in raw.get("prod_orders", []):
            routes = [self._parse_route(r) for r in item.pop("routes", [])]

            journals_raw = item.pop("journals", [])
            journal_routes: list[ProdJournalRouteDTO] = []
            journals: list[ProdJournalDTO] = []

            for j in journals_raw:
                jr_list = j.pop("journal_routes", [])
                journal_routes.extend(self._parse_journal_route(jr) for jr in jr_list)
                journals.append(self._parse_journal(j))

            order = self._parse_order(item)

            aggregates.append(
                ProdOrderAggregateDTO(
                    routes=routes,
                    journals=journals,
                    journal_routes=journal_routes,
                    order=order,
                )
            )

        return aggregates

    def _parse_order(self, data: dict[str, Any]) -> ProdOrderDTO:
        return ProdOrderDTO(
            **self._parse_common_fields(data),
            prod_id=data.pop("prod_id"),
            item_id=data.pop("item_id"),
            name=data.pop("name"),
            prod_group_id=data.pop("prod_group_id"),
            **data,
        )

    def _parse_route(self, data: dict[str, Any]) -> ProdRouteDTO:
        return ProdRouteDTO(
            **self._parse_common_fields(data),
            prod_id=data.pop("prod_id"),
            opr_num=data.pop("opr_num"),
            **data,
        )

    def _parse_journal(self, data: dict[str, Any]) -> ProdJournalDTO:
        return ProdJournalDTO(
            **self._parse_common_fields(data),
            prod_id=data.pop("prod_id", None),
            **data,
        )

    def _parse_journal_route(self, data: dict[str, Any]) -> ProdJournalRouteDTO:
        return ProdJournalRouteDTO(
            **self._parse_common_fields(data),
            prod_id=data.pop("prod_id"),
            journal_id=data.pop("journal_id"),
            **data,
        )

    def _parse_bom(self, data: dict[str, Any]) -> ProdBOMDTO:
        return ProdBOMDTO(
            **self._parse_common_fields(data),
            prod_id=data.pop("prod_id"),
            line_num=data.pop("line_num"),
            **data,
        )

    def _parse_common_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "created_date_time": self._dt(data.pop("created_date_time")),
            "modified_date_time": self._dt(data.pop("modified_date_time")),
        }

    @staticmethod
    def _dt(value: str | None) -> datetime | None:
        return datetime.fromisoformat(value) if value else None

    def _filter(
        self,
        aggregates: list[ProdOrderAggregateDTO],
        *,
        modified_since: str | None,
        prod_ids: list[str] | None,
        limit: int | None,
    ) -> list[ProdOrderAggregateDTO]:

        if modified_since:
            since = datetime.fromisoformat(modified_since)
            aggregates = [
                a
                for a in aggregates
                if a.order.modified_date_time and a.order.modified_date_time > since
            ]

        if prod_ids:
            prod_ids_set = set(prod_ids)
            aggregates = [a for a in aggregates if a.order.prod_id in prod_ids_set]

        if limit is not None:
            aggregates = aggregates[:limit]

        return aggregates
