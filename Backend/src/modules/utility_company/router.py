from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Path, Query, status
from modules.auth.oauth2 import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.db_helper import db_helper

from . import service
from .schemas import (
    AddUtilityCompany,
    ShowOneUtilityCompany,
    ShowUtilityCompany,
    UtilityCompanyUpdate,
)

router = APIRouter(tags=["Комунальні підприємства 🧑‍🏭"], prefix="/utility_company")
SessionDep = Annotated[AsyncSession, Depends(db_helper.session_dependency)]


@router.get(
    "/", response_model=list[ShowUtilityCompany], status_code=status.HTTP_200_OK
)
async def get_all_companies(
    db: SessionDep,
    sort_by_rating: Literal["За зростанням", "За спаданням"] | None = Query(
        None, description="Фільтрація за рейтингом"
    ),
    current_user: dict = Depends(get_current_user),
):
    return await service.get_all(
        current_user=current_user, db=db, sort_by_rating=sort_by_rating
    )


@router.get(
    "/{id}/", response_model=ShowOneUtilityCompany, status_code=status.HTTP_200_OK
)
async def get_one_company_by_id(
    id: Annotated[int, Path(ge=1, lt=10_000)],
    db: SessionDep,
    current_user: dict = Depends(get_current_user),
):
    return await service.get_one(current_user=current_user, id=id, db=db)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_a_new_company(
    request: AddUtilityCompany,
    db: SessionDep,
    current_user: dict = Depends(get_current_user),
):
    return await service.create_company(
        db=db, request=request, current_user=current_user
    )


@router.put("/{id}/", status_code=status.HTTP_200_OK)
async def update_company(
    id: Annotated[int, Path(ge=1, lt=10_000)],
    request: UtilityCompanyUpdate,
    db: SessionDep,
    current_user: dict = Depends(get_current_user),
):
    return await service.update(
        id=id, request=request, db=db, current_user=current_user
    )


@router.delete("/{id}/", status_code=status.HTTP_204_NO_CONTENT)
async def destroy_company(
    id: Annotated[int, Path(ge=1, lt=10_000)],
    db: SessionDep,
    current_user: dict = Depends(get_current_user),
):
    return await service.destroy(id=id, db=db, current_user=current_user)
