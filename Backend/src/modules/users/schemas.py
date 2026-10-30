from datetime import date
from typing import Annotated, Optional

from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, EmailStr


class ImageOut(BaseModel):
    image_id: int
    image_url: str

    model_config = {"from_attributes": True}


class SubscriptionOut(BaseModel):
    subscription_id: Optional[int] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    model_config = {"from_attributes": True}


class BlockingOut(BaseModel):
    reason: str

    model_config = {"from_attributes": True}


class BlockUser(BaseModel):
    user_id: int
    reason: str


class GoogleAuthRequest(BaseModel):
    id_token: str


class UserRegister(BaseModel):
    email: EmailStr
    name: Annotated[str, MinLen(3), MaxLen(35)]
    surname: Annotated[str, MinLen(3), MaxLen(35)]
    password: Annotated[str, MinLen(8), MaxLen(64)]


class UserResponse(BaseModel):
    user_id: int
    email: EmailStr
    name: str
    surname: str


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
