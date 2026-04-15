import re
from typing import Any, TYPE_CHECKING
from fastapi import APIRouter, Depends, HTTPException
from api.core.dependencies.jwt_access import get_user_token, permission_required
from api.core.dependencies.services import (
    get_erm_production_service,
    get_production_service,
)
from api.v1.production.schemas import (
    CreateProdJournalRoute,
    ProdJournalRouteRecordResponse,
    ProdOrderAggregateSchema,
    UpdateProdJournalRoute,
    UpdateProdJournalRouteRecord,
    UpdateProdOrderStatus,
)
from app.core.exceptions.api_exceptions import ApiExceptions
from app.production_journal.models import ProdJournal
from app.production_journal_route_records.models import ProdJournalRouteRecord
from app.production_journal_routes.models import ProdJournalRoute
from app.production_routes.models import ProdRoute
from config.permissions import Permissions

if TYPE_CHECKING:
    from app.production_orders.service import ProductionOrderService
    from integrations.ERM.service import ERMProdOrderLoadService


router = APIRouter()


@router.get(
    "/",
    response_model=list[ProdOrderAggregateSchema],
    dependencies=[permission_required([Permissions.GET_PRODUCTION_ORDERS])],
)
async def get_prod_orders(
    modified_since: str | None = None,
    prod_ids: str | None = None,
    limit: int | None = None,
    service: "ProductionOrderService" = Depends(get_production_service),
) -> list[ProdOrderAggregateSchema]:
    if prod_ids:
        prod_ids = re.split(r"[;,./\\_\s]+", prod_ids)
    prod_orders = await service.get_prod_orders(
        modified_since=modified_since, prod_ids=prod_ids, limit=limit
    )
    return [
        ProdOrderAggregateSchema(
            order=prod_order["order"],
            routes=prod_order["routes"],
            journals=prod_order["journals"],
            journal_routes=prod_order["journal_routes"],
        )
        for prod_order in prod_orders
    ]


@router.get(
    "/{prod_id}",
    dependencies=[permission_required([Permissions.GET_PRODUCTION_ORDERS])],
)
async def get_prod_order_by_id(
    prod_id: str,
    service: "ProductionOrderService" = Depends(get_production_service),
) -> ProdOrderAggregateSchema:
    prod_order = (await service.get_prod_orders(prod_ids=[prod_id]))[0]
    return ProdOrderAggregateSchema(
        order=prod_order["order"],
        routes=prod_order["routes"],
        journals=prod_order["journals"],
        journal_routes=prod_order["journal_routes"],
    )


@router.patch(
    "/{prod_id}/status",
    dependencies=[permission_required([Permissions.UPDATE_PRODUCTION_ORDERS])],
)
async def update_prod_order_status(
    prod_id: str,
    body: UpdateProdOrderStatus,
    service: "ProductionOrderService" = Depends(get_production_service),
) -> ProdOrderAggregateSchema:
    await service.update_prod_order(prod_id, body.model_dump(exclude_unset=True))
    prod_order = (await service.get_prod_orders(prod_ids=[prod_id]))[0]
    return ProdOrderAggregateSchema(
        order=prod_order["order"],
        routes=prod_order["routes"],
        journals=prod_order["journals"],
        journal_routes=prod_order["journal_routes"],
    )


@router.get(
    "/{prod_id}/routes",
    dependencies=[permission_required([Permissions.GET_PRODUCTION_ORDER_ROUTES])],
)
async def get_prod_order_routes(
    prod_id: str, service: "ProductionOrderService" = Depends(get_production_service)
) -> list[ProdRoute]:
    prod_order = (await service.get_prod_orders(prod_ids=[prod_id]))[0]
    return prod_order["routes"]


@router.get(
    "/{prod_id}/routes/{opr_num}",
    dependencies=[permission_required([Permissions.GET_PRODUCTION_ORDER_ROUTES])],
)
async def get_prod_order_route(
    prod_id: str,
    opr_num: int,
    service: "ProductionOrderService" = Depends(get_production_service),
) -> dict[str, Any]:
    return await service.get_prod_order_route_by_opr_num(
        prod_id=prod_id, opr_num=opr_num
    )


@router.get(
    "/{prod_id}/journals",
    dependencies=[permission_required([Permissions.GET_PRODUCTION_ORDER_JOURNALS])],
)
async def get_prod_order_journals(
    prod_id: str, service: "ProductionOrderService" = Depends(get_production_service)
) -> list[ProdJournal]:
    prod_order = (await service.get_prod_orders(prod_ids=[prod_id]))[0]
    return prod_order["journals"]


@router.get(
    "/{prod_id}/journal-routes",
    dependencies=[
        permission_required([Permissions.GET_PRODUCTION_ORDER_JOURNAL_ROUTES])
    ],
)
async def get_prod_order_journal_routes(
    prod_id: str, service: "ProductionOrderService" = Depends(get_production_service)
) -> list[ProdJournalRoute]:
    prod_order = (await service.get_prod_orders(prod_ids=[prod_id]))[0]
    return prod_order["journal_routes"]


@router.post(
    "/{prod_id}/{journal_id}/journal-routes",
    dependencies=[
        permission_required([Permissions.CREATE_PRODUCTION_ORDER_JOURNAL_ROUTES])
    ],
)
async def create_prod_order_journal_routes(
    prod_id: str,
    journal_id: str,
    body: CreateProdJournalRoute,
    user_decode_token: dict = Depends(get_user_token),
    service: "ProductionOrderService" = Depends(get_production_service),
) -> dict[str, Any]:
    username = user_decode_token.get("sub")

    if not username:
        raise ApiExceptions.unauthorized_exception("Invalid token: username not found")

    return await service.create_prod_journal_route(
        prod_id, journal_id, body.model_dump(exclude_unset=True), username
    )


@router.patch(
    "/{prod_id}/{journal_id}/journal-routes/{opr_num}/{line_num}",
    dependencies=[
        permission_required([Permissions.UPDATE_PRODUCTION_ORDER_JOURNAL_ROUTES])
    ],
)
async def update_prod_order_journal_routes(
    prod_id: str,
    journal_id: str,
    opr_num: int,
    line_num: int,
    body: UpdateProdJournalRoute,
    user_decode_token: dict = Depends(get_user_token),
    service: "ProductionOrderService" = Depends(get_production_service),
) -> dict[str, Any]:
    username = user_decode_token.get("sub")

    if not username:
        raise ApiExceptions.unauthorized_exception("Invalid token: username not found")

    return await service.update_prod_journal_router(
        prod_id,
        journal_id,
        opr_num,
        line_num,
        body.model_dump(exclude_unset=True),
        username,
    )


@router.get(
    "/{prod_id}/{journal_id}/{opr_num}/{line_num}/",
    dependencies=[
        permission_required([Permissions.GET_PRODUCTION_ORDER_JOURNAL_ROUTE_RECORDS])
    ],
)
async def get_prod_order_journal_route_records(
    prod_id: str,
    journal_id: str,
    opr_num: int,
    line_num: int,
    service: "ProductionOrderService" = Depends(get_production_service),
) -> list[ProdJournalRouteRecordResponse]:
    return await service.get_journal_route_records(
        prod_id, journal_id, opr_num, line_num
    )


@router.patch(
    "/{journal_route_record_id}",
    dependencies=[
        permission_required([Permissions.UPDATE_PRODUCTION_ORDER_JOURNAL_ROUTE_RECORDS])
    ],
)
async def get_prod_order_journal_route_records(
    journal_route_record_id: int,
    update_data: UpdateProdJournalRouteRecord,
    service: "ProductionOrderService" = Depends(get_production_service),
) -> dict[str, Any]:
    return await service.update_journal_route_record(
        journal_route_record_id, update_data.model_dump(exclude_unset=True)
    )


@router.post(
    "/load-prod-orders-to-db",
    dependencies=[permission_required([Permissions.LOAD_PRODUCTION_ORDERS_TO_DB])],
)
async def load_prod_orders_to_db(
    modified_since: str | None = None,
    prod_ids: str | None = None,
    limit: int | None = None,
    service: "ERMProdOrderLoadService" = Depends(get_erm_production_service),
):
    if prod_ids:
        prod_ids = re.split(r"[;,./\\_\s]+", prod_ids)
    try:
        await service.load_prod_orders_to_db(
            modified_since=modified_since, prod_ids=prod_ids, limit=limit
        )
        return {"status": "OK"}
    except HTTPException:
        raise

    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=str(ex),
        )


@router.post(
    "/{prod_id}/{journal_id}/{opr_num}/{line_num}/finish",
    dependencies=[
        permission_required(
            [
                Permissions.UPDATE_PRODUCTION_ORDER_JOURNAL_ROUTES,
                Permissions.UPDATE_PRODUCTION_ORDERS,
            ]
        )
    ],
)
async def set_prod_order_journal_routes_finished(
    prod_id: str,
    journal_id: str,
    opr_num: int,
    line_num: int,
    user_decode_token: dict = Depends(get_user_token),
    service: "ProductionOrderService" = Depends(get_production_service),
) -> None:
    username = user_decode_token.get("sub")

    if not username:
        raise ApiExceptions.unauthorized_exception("Invalid token: username not found")

    await service.finish_journal_route(prod_id, journal_id, opr_num, line_num, username)
