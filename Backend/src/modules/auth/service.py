# Modules/auth/service.py
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from src.core.models import Admin, User, UtilityCompany
from src.modules.utility_company.schemas import LoginAdminCompanyUser

from .hashing import Hash
from .jwt_handler import create_access_token


async def login(db: AsyncSession, request: LoginAdminCompanyUser):
    # Адмін
    admin_query = select(Admin).where(Admin.email == request.email)
    res_admin = await db.execute(admin_query)
    admin = res_admin.scalars().first()

    if admin:
        if admin.password != request.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний пароль для адміна",
            )
        access_token = create_access_token(data={"sub": admin.email, "role": "admin"})
        return {
            "message": "Успішний вхід ADMIN",
            "admin_surname": admin.surname,
            "access_token": access_token,
            "token_type": "bearer",
        }

    # Компанія
    comp_query = select(UtilityCompany).where(UtilityCompany.email == request.email)
    res_comp = await db.execute(comp_query)
    company = res_comp.scalars().first()

    if company:
        if not Hash.verify(request.password, company.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний пароль для КП",
            )
        access_token = create_access_token(
            data={"sub": company.ut_company_id, "role": "company"}
        )
        return {
            "message": "Успішний вхід COMPANY",
            "company_name": company.name,
            "access_token": access_token,
            "token_type": "bearer",
        }

    # Користувач
    user_query = (
        select(User)
        .options(joinedload(User.image), joinedload(User.blocking))
        .where(User.email == request.email)
    )
    res_user = await db.execute(user_query)
    user = res_user.scalars().first()

    if user:
        if user.blocking:
            raise HTTPException(status_code=400, detail="Користувач уже заблокований")
        if not Hash.verify(request.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Невірний пароль для користувача",
            )

        access_token = create_access_token(data={"sub": user.user_id, "role": "user"})
        return {
            "message": "Успішний вхід USER",
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "name": user.name,
                "surname": user.surname,
                "image": user.image.image_url if user.image else None,
            },
        }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"З email = {request.email} не зареєстровано жодний обліковий запис",
    )
