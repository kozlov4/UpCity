from typing import Annotated, List, Literal, Optional

from annotated_types import MaxLen, MinLen
from core.db_helper import db_helper
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from . import service
from .dependencies import get_current_user
from .schemas import (
    BlockUser,
    GoogleAuthRequest,
    PaymentRequest,
    SubscriptionOut,
    UserRegister,
    UserResponse,
    UserShowAll,
)

router = APIRouter(tags=["Користувач 🧔‍♂️"], prefix="/user")
SessionDep = Annotated[AsyncSession, Depends(db_helper.session_dependency)]


@router.get("/", response_model=List[UserShowAll], status_code=status.HTTP_200_OK)
async def get_all_users(
    db: SessionDep,
    sort_by_subscription: (
        Literal["З підписокою", "Без підписки", "Просрочено"] | None
    ) = Query(None, description="Фільтрація за наявністю підписки"),
    sort_by_rating: Literal["За зростанням", "За спаданням"] | None = Query(
        None, description="Фільтрація за рейтингом"
    ),
    sort_by_name: Literal["А-Я", "Я-А"] | None = Query(
        None, description="Фільтрація за алфавітом"
    ),
    sort_by_blocking: Literal["Заблоковані", "Не заблоковані"] | None = Query(
        None, description="Фільтрація за blocking"
    ),
    current_user: dict = Depends(get_current_user),
):
    return await service.get_all(
        db=db,
        sort_by_subscription=sort_by_subscription,
        sort_by_rating=sort_by_rating,
        sort_by_name=sort_by_name,
        sort_by_blocking=sort_by_blocking,
        current_user=current_user,
    )


@router.get(
    "/subscription/",
    response_model=Optional[SubscriptionOut],
    status_code=status.HTTP_200_OK,
)
async def get_user_subscription_by_user(
    db: SessionDep, current_user: dict = Depends(get_current_user)
):
    return await service.get_sub(db=db, current_user=current_user)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def user_register(request: UserRegister, db: SessionDep):
    response = await service.register(request, db)
    return response["user"]


@router.post("/process_payment")
async def process_payment(
    payment: PaymentRequest,
    db: SessionDep,
    current_user: dict = Depends(get_current_user),
):
    return await service.buy_subscription(
        payment=payment, db=db, current_user=current_user
    )


@router.post("/block/", status_code=status.HTTP_201_CREATED)
async def block_user(
    request: BlockUser, db: SessionDep, current_user: dict = Depends(get_current_user)
):
    return await service.block_user(request=request, db=db, current_user=current_user)


@router.post("/auth/google/")
async def google_login_register(request: GoogleAuthRequest, db: SessionDep):
    return await service.google_auth_reg(request=request, db=db)


@router.put("/me/", status_code=status.HTTP_200_OK)
async def update_user_profile(
    db: SessionDep,
    email: EmailStr = Form(...),
    name: Annotated[str, MinLen(3), MaxLen(35)] = Form(...),
    surname: Annotated[str, MinLen(3), MaxLen(35)] = Form(...),
    image: UploadFile | None = File(None),
    current_user: dict = Depends(get_current_user),
):
    return await service.update_user(
        email=email,
        name=name,
        surname=surname,
        image=image,
        db=db,
        current_user=current_user,
    )
