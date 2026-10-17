from core import get_db
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from repository import authentication_rep
from schemas.utility_company_schemas import LoginAdminCompanyUser
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["Авторизація для | Користувача | Адміна | Кп | 🔓"], prefix="/login"
)


@router.post("/", status_code=status.HTTP_200_OK)
def login(
    request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    email = request.username  # Email —  username in form
    password = request.password

    login_data = LoginAdminCompanyUser(email=email, password=password)

    return authentication_rep.login(db, login_data)
