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

    GET_LOGS = "get_logs"
