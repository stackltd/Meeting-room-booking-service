import os
from typing import AsyncGenerator

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from src.dao import DAO
from src.database import AsyncSessionLocal
from src.exceptions import CredentialsException

# указание на URL для аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)
):
    """Используется для защиты роутов от анонимного доступа. Получение текущего user от username из JWT-токена."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_pwd_version = payload.get("pwd_version")
        username: str = payload.get("sub")
        user: User = await DAO.search_by_fields(User, dict(username=username), db)
        if username is None or user is None:
            raise CredentialsException()

        if user.password_hash[:10] != token_pwd_version:
            raise CredentialsException(detail="Пароль был изменен. Войдите заново.")

        return user
    except jwt.PyJWTError:
        raise CredentialsException()


async def get_admin(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_session)
):
    """Проверка на роль 'admin'"""
    user: User = await get_current_user(token, db)
    if user.role != "admin":
        raise CredentialsException(detail="Доступ запрещён")
    return user
