from fastapi import APIRouter
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.core.config import get_settings
from api.core.dependencies.services import get_auth_service
from api.v1.auth.schemas import Token
from api.v1.auth.service import AuthService


router = APIRouter()

settings = get_settings()


@router.post("/", response_model=Token)
async def login_for_get_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
):

    access_token = await auth_service.create_access_token(
        form_data.username, form_data.password
    )

    return {"access_token": access_token, "token_type": "bearer"}
