from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db_helper import db_helper
from src.modules.utility_company.schemas import LoginAdminCompanyUser

from . import service

router = APIRouter(
    tags=["Авторизація для | Користувача | Адміна | Кп | 🔓"], prefix="/login"
)
SessionDep = Annotated[AsyncSession, Depends(db_helper.session_dependency)]


@router.post("/", status_code=status.HTTP_200_OK)
async def login(
    request: Annotated[OAuth2PasswordRequestForm, Depends()], db: SessionDep
):
    login_data = LoginAdminCompanyUser(
        email=request.username, password=request.password
    )
    return await service.login(db, login_data)
