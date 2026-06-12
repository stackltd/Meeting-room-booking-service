from typing import List

from fastapi import Depends, APIRouter, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.bookings.models import Room, User
from src.bookings.schemas import UserGet, RoomBase, RoomGet
from src.bookings.service import BookingsService
from src.dao import DAO
from src.dependencies import get_session, get_admin, get_current_user
from src.exceptions import CredentialsException


router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get(
    "/users/me",
    description="Профиль пользователя",
    response_model=UserGet,
)
async def get_profile(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    user = await DAO.search_by_field(User, dict(username=current_user.username), db)

    return user


@router.get(
    "/users/{username}",
    description="Поиск пользователя по его username",
    response_model=UserGet,
)
async def get_user(
    username: str = Path(...),
    current_user=Depends(get_admin),
    db: AsyncSession = Depends(get_session),
):
    user = await DAO.search_by_field(User, dict(username=username), db)
    if not user:
        raise CredentialsException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь {username} не найден",
        )

    return user


@router.get(
    "/users", description="Поиск всех пользователей", response_model=List[UserGet]
)
async def get_users(
    current_user=Depends(get_admin), db: AsyncSession = Depends(get_session)
):
    users = await DAO.search_all(User, db)
    if not users:
        raise CredentialsException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователи не найдены",
        )

    return users


@router.post("/rooms", description="Создание комнаты")
async def room_create(
    room_data: RoomBase,
    current_user=Depends(get_admin),
    db: AsyncSession = Depends(get_session),
):
    name = room_data.name
    room = await DAO.search_by_field(Room, dict(name=name), db)
    if room:
        raise CredentialsException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ошибка. Комната {name} уже существует",
        )
    data_dict = room_data.model_dump(exclude_none=True)
    await DAO.add_object(Room, data_dict, db)
    return {"message": f"Комната {name} успешно создана"}


@router.get("/rooms", description="Поиск всех комнат", response_model=List[RoomGet])
async def get_rooms(
    current_user=Depends(get_admin), db: AsyncSession = Depends(get_session)
):
    rooms = await DAO.search_all(Room, db)
    if not rooms:
        raise CredentialsException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Комнаты не найдены",
        )

    return rooms
