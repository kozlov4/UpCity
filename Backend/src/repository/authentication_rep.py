from core import Admin, User, UtilityCompany
from fastapi import HTTPException, status
from hashing import Hash
from jwt_handler import create_access_token
from schemas.utility_company_schemas import LoginAdminCompanyUser
from sqlalchemy.orm import Session


def login(db: Session, request: LoginAdminCompanyUser):
    # Адмін
    admin = db.query(Admin).filter(Admin.email == request.email).first()
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
    company = (
        db.query(UtilityCompany).filter(UtilityCompany.email == request.email).first()
    )
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
    user = db.query(User).filter(User.email == request.email).first()
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
