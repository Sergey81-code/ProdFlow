from enum import StrEnum


class Permissions(StrEnum):
    CREATE_ROLE = "create_role"
    DELETE_ROLE = "delete_role"
    GET_ROLES = "get_roles"
    UPDATE_ROLE = "update_role"

    CREATE_DEVICE = "create_device"
    DELETE_DEVICE = "delete_device"
    GET_DEVICES = "get_devices"
    UPDATE_DEVICE = "update_device"

    CREATE_USER = "create_user"
    DELETE_USER = "delete_user"
    GET_USERS = "get_users"
    UPDATE_USER = "update_user"

    CREATE_DEPARTMENT = "create_department"
    DELETE_DEPARTMENT = "delete_department"
    GET_DEPARTMENTS = "get_departments"
    UPDATE_DEPARTMENT = "update_department"

    CREATE_OPERATION_STAGE = "create operation stage"
    DELETE_OPERATION_STAGE = "delete operation stage"
    GET_OPERATION_STAGES = "get operation stages"
    UPDATE_OPERATION_STAGE = "update operation stage"

    LOAD_PRODUCTION_ORDERS_TO_DB = "load_production_orders_to_db"

    GET_PRODUCTION_ORDERS = "get_production_orders"
    UPDATE_PRODUCTION_ORDERS = "update_production_orders"

    GET_PRODUCTION_ORDER_ROUTES = "get_production_order_routes"

    GET_PRODUCTION_ORDER_JOURNALS = "get_production_order_journals"

    CREATE_PRODUCTION_ORDER_JOURNAL_ROUTES = "create_production_order_journal_routes"
    GET_PRODUCTION_ORDER_JOURNAL_ROUTES = "get_production_order_journal_routes"
    UPDATE_PRODUCTION_ORDER_JOURNAL_ROUTES = "update_production_order_journal_routes"

    GET_PRODUCTION_ORDER_JOURNAL_ROUTE_RECORDS = (
        "get_production_order_journal_route_records"
    )
    UPDATE_PRODUCTION_ORDER_JOURNAL_ROUTE_RECORDS = (
        "update_production_order_journal_route_records"
    )

    GET_LOGS = "get_logs"
