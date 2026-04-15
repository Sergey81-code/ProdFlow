from uuid import UUID

from fastapi import APIRouter, Depends

from api.core.dependencies.jwt_access import get_user_token, permission_required
from api.core.dependencies.services import get_user_service
from app.core.exceptions.api_exceptions import ApiExceptions
from api.v1.users.schemas import CreateUser, ShowUser, UpdateUser
from app.users.service import UserService
from config.permissions import Permissions

router = APIRouter()


@router.get("/me", response_model=ShowUser)
async def get_me(
    user_decode_token: dict = Depends(get_user_token),
    user_service: UserService = Depends(get_user_service),
) -> ShowUser:
    username = user_decode_token.get("sub")

    if not username:
        raise ApiExceptions.unauthorized_exception("Invalid token: username not found")

    return await user_service.get_user_by_username(username)


@router.get(
    "/{user_id}",
    response_model=ShowUser,
    dependencies=[permission_required([Permissions.GET_USERS])],
)
async def get_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
) -> ShowUser:
    return await user_service.get_user_by_id(user_id)


@router.post(
    "/",
    response_model=ShowUser,
    dependencies=[permission_required([Permissions.CREATE_USER])],
)
async def create_user(
    body: CreateUser,
    user_service: UserService = Depends(get_user_service),
) -> ShowUser:
    user_info = body.model_dump(exclude_none=True)
    return await user_service.create_user_in_database(user_info)


@router.patch(
    "/{user_id}",
    response_model=ShowUser,
    dependencies=[permission_required([Permissions.UPDATE_USER])],
)
async def update_user(
    user_id: UUID,
    body: UpdateUser,
    user_service: UserService = Depends(get_user_service),
) -> ShowUser:
    user = await user_service.get_user_by_id(user_id)
    updated_user_info = body.model_dump(exclude_unset=True)
    return await user_service.update_user(user, updated_user_info)


@router.delete(
    "/{user_id}",
    dependencies=[permission_required([Permissions.DELETE_USER])],
)
async def delete_user(
    user_id: UUID,
    user_service: UserService = Depends(get_user_service),
) -> UUID:
    return await user_service.delete_user_by_id(user_id)


@router.get(
    "/",
    response_model=list[ShowUser],
    dependencies=[permission_required([Permissions.GET_USERS])],
)
async def get_users_by_name_or_all(
    name: str | None = None,
    user_service: UserService = Depends(get_user_service),
) -> ShowUser:
    return await user_service.get_user_by_name_or_all(name)
