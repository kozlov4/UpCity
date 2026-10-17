from typing import Annotated

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, EmailStr
from schemas.image_schemas import ImageOut
from schemas.subscription_schemas import SubscriptionOut


class BlockUser(BaseModel):
    user_id: int
    reason: str


class GoogleAuthRequest(BaseModel):
    id_token: str


class BlockingOut(BaseModel):
    reason: str


class UserRegister(BaseModel):
    email: EmailStr
    name: Annotated[str, MinLen(3), MaxLen(35)]
    surname: Annotated[str, MinLen(3), MaxLen(35)]
    password: Annotated[str, MinLen(8), MaxLen(64)]


class UserShowAll(BaseModel):
    user_id: int
    name: str
    surname: str
    email: EmailStr
    rating: float | None = 0
    image: ImageOut | None = None
    subscription: SubscriptionOut | None = None
    blocking: BlockingOut | None = None

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    message: str


class PaymentRequest(BaseModel):
    paymentToken: str
