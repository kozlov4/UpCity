from fastapi import Depends, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,  # FastAPI-шний механізм для витягування токена з Authorization заголовку (Bearer <token>).
)
from jwt_handler import (
    verify_token,  # функції з jwt_handler, які кодують/декодують токени
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")


# def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Невалідні облікові дані",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     user_data = verify_token(token)
#     if user_data is None:
#         raise credentials_exception
#     return user_data
def get_current_user(token: str = Depends(oauth2_scheme)):
    print(f"[DEBUG] Отримано токен: {token}")

    user_data = verify_token(token)
    print(f"[DEBUG]  Розпаковані дані токена: {user_data}")

    if user_data is None:
        print("[ERROR] Токен недействительный!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалідні облікові дані",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверка на наличие sub и его тип
    if "sub" not in user_data or not isinstance(user_data["sub"], str):
        print("[ERROR] Поле 'sub' отсутствует или не строка!")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалідні облікові дані: отсутствует или некорректное поле 'sub'",
        )

    return user_data
