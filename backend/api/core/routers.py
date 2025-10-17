from fastapi import APIRouter

from api.v1.auth.handlers import router as auth_router
from api.v1.devices.handlers import router as device_router
from api.v1.users.handlers import router as user_router
from api.v1.roles.handlers import router as role_router


router = APIRouter()

api_v1 = APIRouter(prefix="/v1")

api_v1.include_router(auth_router, prefix="/auth", tags=["auth"])
api_v1.include_router(device_router, prefix="/devices", tags=["devices"])
api_v1.include_router(user_router, prefix="/users", tags=["users"])
api_v1.include_router(role_router, prefix="/roles", tags=["roles"])


router.include_router(api_v1)
