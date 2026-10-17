from typing import List, Literal, Annotated, Optional

from fastapi import APIRouter, Depends, status, Query, UploadFile, Form, File
from sqlalchemy.orm import Session
from annotated_types import MinLen, MaxLen
from pydantic import EmailStr

from project.core.database import get_db
from project.schemas.user_schemas import UserRegister , UserShowAll , BlockUser, PaymentRequest, GoogleAuthRequest
from project.schemas.subscription_schemas import SubscriptionOut
from project.repository import user_rep
from project.oauth2 import get_current_user



router = APIRouter(tags=['Користувач🧔‍♂️'], prefix='/user')


@router.get(
    "/",
    response_model=List[UserShowAll],
    status_code=status.HTTP_200_OK
)
def get_all_users(
    db: Session = Depends(get_db),
    sort_by_subscription: Literal["З підписокою", "Без підписки", "Просрочено"] | None = Query(
        None, description="Фільтрація за наявністю підписки"
    ),
    sort_by_rating: Literal["За зростанням", "За спаданням"] | None = Query(
        None, description="Фільтрація за рейтингом"
    ),
    sort_by_name: Literal["А-Я", "Я-А"] | None = Query(
        None, description="Фільтрація за алфавітом"
    ),
    sort_by_blocking: Literal["Заблоковані", "Не заблоковані"] | None = Query(
        None, description="Фільтрація за blocking"
    ),
    current_user: dict = Depends(get_current_user)
):
    return user_rep.get_all(
        db=db,
        sort_by_subscription=sort_by_subscription,
        sort_by_rating=sort_by_rating,
        sort_by_name=sort_by_name,
        sort_by_blocking=sort_by_blocking,
        current_user=current_user
    )



@router.get(
    "/subscription/",
    response_model=Optional[SubscriptionOut],
    status_code=status.HTTP_200_OK
)
def get_user_subscription_by_user(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return user_rep.get_sub(
        db=db,
        current_user=current_user
    )




@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED
)
def user_register(
    request: UserRegister, 
    db:Session = Depends(get_db)
    ):
    return user_rep.register(
        request, 
        db
    )



@router.post("/process_payment")
async def process_payment(
    payment: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return user_rep.buy_subscription(
        payment=payment,
        db=db,
        current_user=current_user
    )



@router.post(
    "/block/", 
    status_code=status.HTTP_201_CREATED
)
def block_user(
    request: BlockUser, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
    ):
    return user_rep.block_user(
        request = request, 
        db = db, 
        current_user=current_user
    )



@router.post("/auth/google/")
def google_login_regiser(
    request: GoogleAuthRequest, 
    db: Session = Depends(get_db)
    ):
    return user_rep.google_auth_reg(
        request=request,
        db=db
    )



@router.put("/me/", status_code=status.HTTP_200_OK)
def update_user_profile(
    email: EmailStr = Form(...),
    name: Annotated[str, MinLen(3), MaxLen(35)] = Form(...),
    surname: Annotated[str, MinLen(3), MaxLen(35)] = Form(...),
    image: UploadFile | str | None = File(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if image == "" or image is None:
        image = None

    return user_rep.update_user(
        email=email,
        name=name,
        surname=surname,
        image=image,
        db=db,
        current_user=current_user
    )
