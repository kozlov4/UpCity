# service.py
import os
from datetime import date, timedelta
from typing import Literal

from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from repository.image_rep import upload
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from .models import Blocking, Subscription, User
from .schemas import BlockUser, GoogleAuthRequest, PaymentRequest, UserRegister
from .utils import encode_jwt, hash_password

load_dotenv()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


async def get_all(
    db: AsyncSession,
    sort_by_subscription: Literal["З підписокою", "Без підписки", "Просрочено"] | None,
    sort_by_rating: Literal["За зростанням", "За спаданням"] | None,
    sort_by_name: Literal["А-Я", "Я-А"] | None,
    sort_by_blocking: Literal["Заблоковані", "Не заблоковані"] | None,
    current_user: dict,
):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    query = select(User).options(
        joinedload(User.subscription), joinedload(User.blocking)
    )

    if sort_by_subscription == "З підписокою":
        query = query.join(User.subscription).where(Subscription.status == "Активна")
    elif sort_by_subscription == "Без підписки":
        query = query.where(User.subscription_id.is_(None))
    elif sort_by_subscription == "Просрочено":
        query = query.join(User.subscription).where(Subscription.status == "Неактивна")

    if sort_by_blocking == "Не заблоковані":
        query = query.where(User.blocking.is_(None))
    elif sort_by_blocking == "Заблоковані":
        query = query.where(User.blocking.is_not(None))

    if sort_by_rating == "За зростанням":
        query = query.order_by(asc(User.rating))
    elif sort_by_rating == "За спаданням":
        query = query.order_by(desc(User.rating))

    if sort_by_name == "А-Я":
        query = query.order_by(asc(User.name))
    elif sort_by_name == "Я-А":
        query = query.order_by(desc(User.name))

    result = await db.execute(query)
    return result.scalars().all()


async def get_sub(db: AsyncSession, current_user: dict):
    if current_user.get("role") != "user":
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Не вдалося визначити користувача")

    query = (
        select(User)
        .options(joinedload(User.subscription))
        .where(User.user_id == user_id)
    )
    result = await db.execute(query)
    user = result.scalars().first()

    if not user or not user.subscription:
        return None

    return user.subscription


async def register(request: UserRegister, db: AsyncSession):
    query = (
        select(User)
        .options(joinedload(User.blocking), joinedload(User.image))
        .where(User.email == request.email)
    )
    result = await db.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        if existing_user.blocking:
            raise HTTPException(status_code=400, detail="Користувач уже заблокований")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Користувач з email = {request.email} вже існує",
        )

    new_user = User(
        email=request.email,
        name=request.name,
        surname=request.surname,
        password=hash_password(request.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access_token = encode_jwt(
        payload={"sub": str(new_user.user_id), "type": "access", "role": "user"}
    )

    return {
        "message": "Успішна реєстрація",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": new_user.user_id,
            "email": new_user.email,
            "name": new_user.name,
            "surname": new_user.surname,
        },
    }


async def buy_subscription(
    payment: PaymentRequest, db: AsyncSession, current_user: dict
):
    if current_user.get("role") != "user":
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Не вдалося визначити користувача")

    query = (
        select(User)
        .options(joinedload(User.subscription))
        .where(User.user_id == user_id)
    )
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Користувач не знайдений")

    if user.subscription and user.subscription.status == "Активна":
        raise HTTPException(status_code=429, detail="У вас вже є активна підписка.")

    if payment.paymentToken == "examplePaymentMethodToken":
        today = date.today()
        new_sub = Subscription(
            status="Активна", start_date=today, end_date=today + timedelta(days=30)
        )
        db.add(new_sub)
        await db.flush()

        user.subscription_id = new_sub.subscription_id
        await db.commit()

        return {
            "status": "success",
            "subscription_id": new_sub.subscription_id,
            "message": "Оплата пройшла успішно (тестовий режим)",
        }

    return {"status": "error", "message": "Невірний тестовий токен"}


async def block_user(request: BlockUser, db: AsyncSession, current_user: dict):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    query = (
        select(User)
        .options(joinedload(User.blocking))
        .where(User.user_id == request.user_id)
    )
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    if user.blocking:
        raise HTTPException(status_code=400, detail="Користувач уже заблокований")

    block = Blocking(user_id=request.user_id, reason=request.reason)
    db.add(block)
    await db.commit()

    return {"message": "Користувача заблоковано"}


async def google_auth_reg(request: GoogleAuthRequest, db: AsyncSession):
    try:
        idinfo = id_token.verify_oauth2_token(
            request.id_token, google_requests.Request(), GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")
        name = idinfo.get("given_name", "")
        surname = idinfo.get("family_name", "")
        picture_url = idinfo.get("picture", None)

        if not email:
            raise HTTPException(
                status_code=400, detail="Не вдалося отримати email з Google"
            )

        query = (
            select(User)
            .options(joinedload(User.image), joinedload(User.blocking))
            .where(User.email == email)
        )
        result = await db.execute(query)
        user = result.scalars().first()

        # Assuming `Image` model exists in `src.modules.application.models`
        from src.modules.application.models import Image

        if user:
            if user.blocking:
                raise HTTPException(status_code=400, detail="Користувач заблокований")

            if not user.image and picture_url:
                image = Image(image_url=picture_url)
                db.add(image)
                await db.flush()
                user.image_id = image.image_id
                await db.commit()
                await db.refresh(user)
        else:
            image = None
            if picture_url:
                image = Image(image_url=picture_url)
                db.add(image)
                await db.flush()

            user = User(
                email=email,
                name=name,
                surname=surname,
                password=hash_password("google"),
                image_id=image.image_id if image else None,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        access_token = encode_jwt(
            payload={"sub": str(user.user_id), "type": "access", "role": "user"}
        )

        return {
            "message": "Успішна авторизація через Google",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "name": user.name,
                "surname": user.surname,
                "email": user.email,
                "image": user.image.image_url if user.image else None,
            },
        }

    except ValueError:
        raise HTTPException(status_code=401, detail="Невірний Google токен")
    except Exception:
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера")


async def update_user(
    email: str,
    name: str,
    surname: str,
    image: UploadFile | None,
    db: AsyncSession,
    current_user: dict,
):
    if current_user.get("role") != "user":
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Не вдалося визначити користувача")

    query = select(User).options(joinedload(User.image)).where(User.user_id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    email_query = (
        select(User).options(joinedload(User.blocking)).where(User.email == email)
    )
    email_result = await db.execute(email_query)
    existing_user = email_result.scalars().first()

    if existing_user and existing_user.user_id != user.user_id:
        if existing_user.blocking:
            raise HTTPException(
                status_code=400, detail="Користувач з таким email заблокований"
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Користувач з email = {email} вже існує",
        )

    user.email = email
    user.name = name
    user.surname = surname

    if image:
        upload_result = upload(image)
        image_id = upload_result.get("image_id")
        if image_id:
            user.image_id = image_id

    await db.commit()
    await db.refresh(user)

    return {
        "message": "Дані оновлено",
        "user": {
            "name": user.name,
            "surname": user.surname,
            "email": user.email,
            "image": user.image.image_url if user.image else None,
        },
    }
