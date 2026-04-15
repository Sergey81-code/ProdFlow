from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from app.core.exceptions.api_exceptions import ApiExceptions
from app.core.exceptions.db_exceptions import DbExceptions

from app.production_journal_route_records.models import ProdJournalRouteRecord
from app.production_journal_routes.models import ProdJournalRoute
from app.production_routes.models import ProdRoute
from config.actions import Actions


if TYPE_CHECKING:
    from app.production_journal.repo_interface import IProdJournalRepository
    from app.production_journal_routes.repo_interface import IProdJournalRouteRepository
    from app.production_orders.repo_interface import IProdOrderRepository
    from app.production_routes.repo_interface import IProdRouteRepository
    from app.production_journal_route_records.repo_interface import (
        IProdJournalRouteRecordRepository,
    )
    from app.users.repo_interface import IUserRepository


class ProductionOrderService:
    def __init__(
        self,
        order_repo: "IProdOrderRepository",
        route_repo: "IProdRouteRepository",
        journal_repo: "IProdJournalRepository",
        journal_route_repo: "IProdJournalRouteRepository",
        journal_route_record_repo: "IProdJournalRouteRecordRepository",
        user_repo: "IUserRepository",
    ):
        self._order_repo: "IProdOrderRepository" = order_repo
        self._route_repo: "IProdRouteRepository" = route_repo
        self._journal_repo: "IProdJournalRepository" = journal_repo
        self._journal_route_repo: "IProdJournalRouteRepository" = journal_route_repo
        self._journal_route_record_repo: "IProdJournalRouteRecordRepository" = (
            journal_route_record_repo
        )
        self._user_repo: "IUserRepository" = user_repo

    async def get_prod_orders(
        self,
        modified_since: str | None = None,
        prod_ids: list[str] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        try:
            result: list[dict[str, Any]] = []

            prod_orders = await self._order_repo.list_all(
                modified_since=modified_since, prod_ids=prod_ids, limit=limit
            )

            for prod_order in prod_orders:
                routes = await self._route_repo.list_by_order(
                    prod_id=prod_order.prod_id
                )

                journals = await self._journal_repo.list_by_order(
                    prod_id=prod_order.prod_id
                )

                journal_routes = await self._journal_route_repo.list_by_order(
                    prod_id=prod_order.prod_id
                )

                result.append(
                    {
                        "order": prod_order,
                        "routes": routes,
                        "journals": journals,
                        "journal_routes": journal_routes,
                    }
                )
            if result:
                return result
            raise ApiExceptions.not_found_exception("Production order(s) not found")
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def get_prod_order_route_by_opr_num(
        self, prod_id: str, opr_num: int
    ) -> dict[str, Any]:
        try:
            order_routes = await self._route_repo.list_by_order(prod_id)
            for order_route in order_routes:
                if order_route.opr_num == opr_num:
                    return order_route.model_dump()

            raise ApiExceptions.not_found_exception(
                f"Production route in production order {prod_id} with operaton number {opr_num} not found"
            )
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def update_prod_order(
        self, prod_id: str, update_data: dict[str, Any]
    ) -> None:
        try:
            if not update_data:
                raise ApiExceptions.validation_exception(
                    "At least one parameter must be defined"
                )
            update_data["modified_date_time"] = datetime.now()
            await self._order_repo.update_order(prod_id, update_data)
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def create_prod_journal_route(
        self, prod_id: str, journal_id: str, create_data: dict[str, Any], username: str
    ) -> dict[str, Any]:
        try:
            journal_route = ProdJournalRoute(
                prod_id=prod_id, journal_id=journal_id, **create_data
            )
            journal_route.created_date_time = datetime.now()
            journal_route.modified_date_time = datetime.now()
            journal_route.from_time = datetime.now().time()

            user = (
                await self._user_repo.get_by_username(
                    username, exact_match=True, case_sensitive=True
                )
            )[0]
            if not user:
                raise ApiExceptions.not_found_exception("User not found")

            journal_route.user_id = user.id

            journal_route_record = ProdJournalRouteRecord(
                user_id=user.id,
                prod_id=prod_id,
                journal_id=journal_id,
                opr_num=create_data.get("opr_num"),
                line_num=create_data.get("line_num", 1),
                action=Actions.CREATION,
                record_date=datetime.now().date(),
                record_time=datetime.now().time(),
                created_date_time=datetime.now()
                .astimezone(timezone.utc)
                .replace(tzinfo=None),
            )

            created_journal_route = (
                await self._journal_route_repo.upsert([journal_route])
            )[0]
            await self._journal_route_record_repo.create(journal_route_record)
            return created_journal_route.model_dump()

        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def update_prod_router(
        self, prod_id: str, opr_num: int, update_data: dict[str, Any]
    ) -> dict[str, Any]:
        try:
            route = self._route_repo.get(prod_id, opr_num)
            if route is None:
                raise ApiExceptions.not_found_exception("Route not found")
            update_route = ProdRoute(prod_id=prod_id, opr_num=opr_num, **update_data)
            update_route.modified_date_time = datetime.now()
            updated_route = (await self._route_repo.upsert_many([update_route]))[0]
            return updated_route.model_dump()
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def update_prod_journal_router(
        self,
        prod_id: str,
        journal_id: str,
        opr_num: int,
        line_num: int,
        update_data: dict[str, Any],
        username: str,
    ) -> dict[str, Any]:
        try:
            journal_route = self._journal_route_repo.get(
                prod_id, journal_id, opr_num, line_num
            )

            if journal_route is None:
                raise ApiExceptions.not_found_exception("Journal route not found")

            update_journal_route = ProdJournalRoute(
                prod_id=prod_id,
                journal_id=journal_id,
                opr_num=opr_num,
                line_num=line_num,
                **update_data,
            )
            update_journal_route.modified_date_time = datetime.now()

            user = (
                await self._user_repo.get_by_username(
                    username, exact_match=True, case_sensitive=True
                )
            )[0]
            if not user:
                raise ApiExceptions.not_found_exception("User not found")

            journal_route_record = ProdJournalRouteRecord(
                user_id=user.id,
                prod_id=prod_id,
                journal_id=journal_id,
                opr_num=opr_num,
                line_num=line_num,
            )
            journal_route_record.action = Actions.UPDATING
            journal_route_record.record_date = datetime.now().date()
            journal_route_record.record_time = datetime.now().time()
            journal_route_record.created_date_time = datetime.now()

            updated_journal_route = (
                await self._journal_route_repo.upsert([update_journal_route])
            )[0]
            return updated_journal_route.model_dump()
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def finish_journal_route(
        self,
        prod_id: str,
        journal_id: str,
        opr_num: int,
        line_num: int,
        username: str,
    ) -> None:
        fields_to_update_for_journal_route = {
            "opr_finished": True,
            "job_finished": True,
            "executed_pct": 100,
            "to_time": datetime.now().time(),
        }

        fields_to_update_for_route = {
            "opr_finished": True,
            "to_date": datetime.now().date(),
        }

        await self.update_prod_journal_router(
            prod_id,
            journal_id,
            opr_num,
            line_num,
            fields_to_update_for_journal_route,
            username,
        )
        await self.update_prod_router(prod_id, opr_num, fields_to_update_for_route)

    async def get_journal_route_records(
        self,
        prod_id: str,
        journal_id: str,
        opr_num: int,
        line_num: int,
    ) -> list[dict[str, Any]]:
        try:
            journal_route_records: list[ProdJournalRouteRecord] = (
                await self._journal_route_record_repo.get(
                    prod_id, journal_id, opr_num, line_num
                )
            )

            if not journal_route_records:
                return []

            users = await self._user_repo.get_all()

            user_map = {user.id: user.username for user in users}

            result: list[dict[str, Any]] = []
            for jr in journal_route_records:
                data = jr.model_dump()
                data["username"] = user_map.get(jr.user_id)
                result.append(data)

            return result

        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")

    async def update_journal_route_record(
        self, journal_route_record_id: int, update_data: dict[str, Any]
    ) -> dict[str, Any]:
        try:
            journal_route_record = await self._journal_route_record_repo.get_by_id(
                journal_route_record_id
            )
            if not journal_route_record:
                raise ApiExceptions.not_found_exception(
                    "Journal route record not found"
                )

            updated_journal_route_record: ProdJournalRouteRecord = (
                await self._journal_route_record_repo.update(
                    journal_route_record, update_data
                )
            )
            return updated_journal_route_record.model_dump()
        except DbExceptions.exc_class():
            raise ApiExceptions.service_unavailable_exception("Database error.")
