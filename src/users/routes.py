from fastapi import Depends, APIRouter, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from src.users.schemas import UserGet
from src.dao import DAO
from src.dependencies import get_session, get_admin, get_current_user
from src.users.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    description="Профиль пользователя",
    response_model=UserGet,
)
async def get_profile(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    user = await DAO.search_by_fields(User, dict(username=current_user.username), db)
    return user


@router.get(
    "/{username}",
    description="Поиск пользователя по его username",
    response_model=UserGet,
)
async def get_user(
    username: str = Path(...),
    current_user=Depends(get_admin),
    db: AsyncSession = Depends(get_session),
):
    user = await UserService.search_user(username, db)
    return user


@router.get("", description="Поиск всех пользователей", response_model=list[UserGet])
async def get_users(
    current_user=Depends(get_admin), db: AsyncSession = Depends(get_session)
):
    users = await DAO.search_all(User, db)
    return users
