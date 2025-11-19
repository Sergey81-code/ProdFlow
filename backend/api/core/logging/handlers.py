import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from api.core.dependencies.jwt_access import permission_required
from config.permissions import Permissions

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
LOG_DIR = os.path.join(BASE_DIR, "logs")

log_router = APIRouter(prefix="/logs", tags=["logs"])


@log_router.get("/", dependencies=[permission_required([Permissions.GET_LOGS])])
async def list_logs():
    if not os.path.exists(LOG_DIR):
        return []

    files = [f for f in os.listdir(LOG_DIR) if os.path.isfile(os.path.join(LOG_DIR, f))]
    return {"logs": files}


@log_router.get(
    "/{log_filename}", dependencies=[permission_required([Permissions.GET_LOGS])]
)
async def get_log_file(log_filename: str):
    file_path = os.path.join(LOG_DIR, log_filename)

    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Log file not found")
    if os.path.commonpath([os.path.realpath(file_path), LOG_DIR]) != os.path.realpath(
        LOG_DIR
    ):
        raise HTTPException(status_code=403, detail="Access denied")

    return FileResponse(file_path, media_type="text/plain", filename=log_filename)
