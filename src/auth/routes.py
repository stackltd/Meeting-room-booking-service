import logging

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import UserCreate, PasswordChange, UserUpdate

from src.auth.service import AuthService

from src.dependencies import get_session, get_current_user, get_admin

router = APIRouter(prefix="/auth", tags=["Auth"])

logger = logging.getLogger("app")


@router.post("/register")
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_session)):
    """Регистрация нового пользователя."""
    await AuthService.make_user(user_data, db)
    message = f"Пользователь {user_data.username} успешно зарегистрирован"
    logger.info(message)
    return {"message": message}


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """Получение JWT-токена по логину (username/email) и паролю."""
    access_token = await AuthService.make_token(form_data, db)
    return {"access_token": access_token, "token_type": "bearer"}


@router.patch("/change/password")
async def change_password(
    passwords: PasswordChange,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Смена пароля текущего пользователя"""
    await AuthService.change_password(passwords, current_user, db)
    message = f"Пароль для {current_user.username} успешно изменён"
    logger.info(message)
    return {"message": message}


@router.patch("/change/user")
async def change_user(
    user_data: UserUpdate,
    current_user=Depends(get_admin),
    db: AsyncSession = Depends(get_session),
):
    """Изменение данных любого пользователя"""
    await AuthService.change_user(user_data, db)
    message = f"{current_user.username} успешно изменил данные пользователя {user_data.username}"
    logger.info(message)
    return {"message": message}
