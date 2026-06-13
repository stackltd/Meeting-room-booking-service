from datetime import date

from fastapi import Depends, APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.bookings.models import Room
from src.users.models import User
from src.bookings.schemas import (
    RoomBase,
    RoomGet,
    BookingCreate,
    UserWithBookingsGet,
    RoomWithFreeSlotsGet,
)
from src.bookings.service import BookingsService
from src.dao import DAO
from src.dependencies import get_session, get_admin, get_current_user


router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/rooms", description="Создание комнаты")
async def room_create(
    room_data: RoomBase,
    current_user=Depends(get_admin),
    db: AsyncSession = Depends(get_session),
):
    await BookingsService.room_create(room_data, db)
    return {"message": f"Комната {room_data.name} успешно создана"}


@router.get("/rooms", description="Поиск всех комнат", response_model=list[RoomGet])
async def get_rooms(db: AsyncSession = Depends(get_session)):
    rooms = await DAO.search_all(Room, db)
    return rooms


@router.post("")
async def create_booking(
    booking_data: BookingCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    await BookingsService.create_booking(booking_data, current_user, db)
    return {
        "message": f"Комната {booking_data.room_id} забронирована на дату {booking_data.booking_date} на интервал {booking_data.time_slot}"
    }


@router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    await BookingsService.cancel_booking(booking_id, current_user, db)

    return {"status": "success", "message": "Бронирование успешно отменено"}


@router.get("/users-current-bookings", response_model=list[UserWithBookingsGet])
async def get_active_users(
    current_user=Depends(get_admin), db: AsyncSession = Depends(get_session)
):
    users = await DAO.get_users_with_active_bookings(db)
    return users


@router.get("/room-available", response_model=list[RoomWithFreeSlotsGet])
async def get_available_rooms(
    booking_date: date = Query(..., description="Дата проверки (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_session),
):
    rooms = await BookingsService.get_available_rooms(booking_date, db)
    return rooms
