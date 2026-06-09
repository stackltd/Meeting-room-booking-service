from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.schemas import UserCreate

from src.database import get_session


from src.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_session)):
    """Регистрация нового пользователя."""
    async with db.begin():
        # проверка существования пользователя с username
        user = await AuthService.get_user(user_data.username, db)
        if user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с данным username уже существует. Выберите другое имя",
            )
        # создаем нового пользователя
        await AuthService.make_user(user_data, db)
        return {"message": "Пользователь успешно зарегистрирован"}


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    """Получение JWT-токена по логину (username/email) и паролю."""
    access_token = await AuthService.make_token(form_data, db)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/test_auth_from_token")
async def get_secure_data(
    current_user_username: str = Depends(AuthService.get_username_from_token),
):
    # Тест доступа через JWT."""
    return {
        "message": f"{current_user_username}",
        "status": "Доступ разрешен",
    }
