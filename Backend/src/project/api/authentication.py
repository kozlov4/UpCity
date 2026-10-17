from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from fastapi.security import  OAuth2PasswordRequestForm

from project.core.database import get_db
from project.repository import authentication_rep
from project.schemas.utility_company_schemas import LoginAdminCompanyUser


router = APIRouter(
            tags=['Авторизація для | Користувача | Адміна | Кп | 🔓'], 
            prefix="/login"
            )


@router.post(
    "/", 
    status_code=status.HTTP_200_OK
)
def login(
    request: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    
    email = request.username # Email —  username in form
    password = request.password

    login_data = LoginAdminCompanyUser(
        email=email, 
        password=password
    )

    return authentication_rep.login(db, login_data)

