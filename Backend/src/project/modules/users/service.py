import os
from datetime import date, timedelta
from typing import Literal

from dotenv import load_dotenv
from fastapi import HTTPException, UploadFile, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from project.core.models import Blocking, Image, Subscription, User
from project.hashing import Hash
from project.jwt_handler import create_access_token
from project.repository.image_rep import upload
from sqlalchemy import asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, joinedload

load_dotenv()


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


def get_all(
    db: AsyncSession,
    sort_by_subscription: Literal["З підписокою", "Без підписки", "Просрочено"] | None,
    sort_by_rating: Literal["За зростанням", "За спаданням"] | None,
    sort_by_name: Literal["А-Я", "Я-А"] | None,
    sort_by_blocking: Literal["Заблоковані", "Не заблоковані"] | None,
    current_user: dict,
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Недостатньо прав")
    query = db.query(User)

    if sort_by_subscription == "З підписокою":
        query = query.join(User.subscription).filter(Subscription.status == "Активна")
    elif sort_by_subscription == "Без підписки":
        query = query.filter(User.subscription_id == None)
    elif sort_by_subscription == "Просрочено":
        query = query.join(User.subscription).filter(Subscription.status == "Неактивна")

    if sort_by_blocking == "Не заблоковані":
        query = query.filter(User.blocking == None)
    elif sort_by_blocking == "Заблоковані":
        query = query.filter(User.blocking != None)

    if sort_by_rating == "За зростанням":
        query = query.order_by(asc(User.rating))
    elif sort_by_rating == "За спаданням":
        query = query.order_by(desc(User.rating))

    if sort_by_name == "А-Я":
        query = query.order_by(asc(User.name))

    elif sort_by_name == "Я-А":
        query = query.order_by(desc(User.name))

    users = query.all()
    return users


def get_sub(db: AsyncSession, current_user: dict):
    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Не вдалося визначити користувача")

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .outerjoin(User.subscription)
        .first()
    )

    if not user or not user.subscription:
        return None

    return user.subscription


def register(request: UserRegister, db: AsyncSession):
    existing_user = db.query(User).filter(User.email == request.email).first()

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
        password=Hash.bcrypt(request.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token(data={"sub": new_user.user_id, "role": "user"})

    return {
        "message": "Успішна реєстрація",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "name": new_user.name,
            "surname": new_user.surname,
            "image": new_user.image.image_url if new_user.image else None,
        },
    }


def buy_subscription(payment: PaymentRequest, db: AsyncSession, current_user: dict):

    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Не вдалося визначити користувача")

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .outerjoin(User.subscription)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="Користувач не знайдений")

    has_active_subscription = (
        user.subscription is not None and user.subscription.status == "Активна"
    )

    if has_active_subscription:
        raise HTTPException(status_code=429, detail="У вас вже є активна підписка.")

    payment_token = payment.paymentToken

    if payment_token == "examplePaymentMethodToken":
        # 1. Створюємо підписку
        today = date.today()
        new_sub = Subscription(
            status="Активна", start_date=today, end_date=today + timedelta(days=30)
        )
        db.add(new_sub)
        db.commit()
        db.refresh(new_sub)

        # 2. Прив'язуємо користувача до підписки
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Користувача не знайдено")

        user.subscription_id = new_sub.subscription_id
        db.commit()

        return {
            "status": "success",
            "subscription_id": new_sub.subscription_id,
            "message": "Оплата пройшла успішно (тестовий режим)",
        }
    else:
        return {"status": "error", "message": "Невірний тестовий токен"}


def block_user(request: BlockUser, db: AsyncSession, current_user: dict):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Недостатньо прав")
    user = db.query(User).filter(User.user_id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    if user.blocking:
        raise HTTPException(status_code=400, detail="Користувач уже заблокований")

    block = Blocking(user_id=request.user_id, reason=request.reason)
    db.add(block)
    db.commit()
    db.refresh(block)
    return {"message": "Користувача заблоковано"}


def google_auth_reg(request: GoogleAuthRequest, db: AsyncSession):
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

        user = (
            db.query(User)
            .options(joinedload(User.image))
            .filter(User.email == email)
            .first()
        )

        if user:
            if user.blocking:
                raise HTTPException(status_code=400, detail="Користувач заблокований")

            if not user.image and picture_url:
                print("Користувач не має фото. Додаємо нове Image.")
                image = Image(image_url=picture_url)
                db.add(image)
                db.flush()
                user.image_id = image.image_id
                db.commit()
                db.refresh(user)
        else:
            print("Користувача немає, створюємо нового.")
            image = None
            if picture_url:
                print("Створення нового об'єкта Image.")
                image = Image(image_url=picture_url)
                db.add(image)
                db.flush()
                print("Image створено з ID:", image.image_id)
            else:
                print("Фото відсутнє, не створюємо Image.")

            user = User(
                email=email,
                name=name,
                surname=surname,
                password=Hash.bcrypt("google"),
                image_id=image.image_id if image else None,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print("Новий користувач створений з ID:", user.user_id)

        access_token = create_access_token(data={"sub": user.user_id, "role": "user"})

        print("Авторизація успішна.")
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
        print("Помилка перевірки токена.")
        raise HTTPException(status_code=401, detail="Невірний Google токен")
    except Exception as e:
        print("Невідома помилка:", e)
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера")


def update_user(
    email: str,
    name: str,
    surname: str,
    image: UploadFile | None,
    db: AsyncSession,
    current_user: dict,
):
    if current_user["role"] != "user":
        raise HTTPException(status_code=403, detail="Недостатньо прав")

    user_id = current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Не вдалося визначити користувача")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    existing_user = db.query(User).filter(User.email == email).first()

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

    db.commit()
    db.refresh(user)

    return {
        "message": "Дані оновлено",
        "user": {
            "name": user.name,
            "surname": user.surname,
            "email": user.email,
            "image": user.image.image_url if user.image else None,
        },
    }
