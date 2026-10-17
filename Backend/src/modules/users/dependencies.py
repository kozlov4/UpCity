import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.modules.users.utils import decode_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")

oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="api/v1/login", auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> int:
    try:
        payload = decode_jwt(token)

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type. An access token is required for access.",
            )

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The token does not contain a user ID",
            )

        return int(user_id_str)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The token has expired. Please refresh the token.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
        )


async def get_current_user_optional(
    token: str | None = Depends(oauth2_scheme_optional),
) -> int | None:
    if not token:
        return None

    return await get_current_user(token)
