# Modules/auth/oauth2.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .jwt_handler import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user_data = verify_token(token)

    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалідні облікові дані",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if "sub" not in user_data or not isinstance(user_data["sub"], str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалідні облікові дані: некоректне поле 'sub'",
        )

    return user_data
