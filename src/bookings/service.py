import logging
from datetime import date
from starlette import status

from src.bookings.models import Room, Booking
from src.dao import DAO
from src.exceptions import CredentialsException
from src.settings import ALLOWED_SLOTS

logger = logging.getLogger("app")


class BookingsService:

    @classmethod
    async def room_create(cls, room_data, db):
        name = room_data.name
        room = await DAO.search_by_fields(Room, dict(name=name), db)
        if room:
            message = f"Ошибка. Комната {name} уже существует"
            logger.warning(message)
            raise CredentialsException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )
        data_dict = room_data.model_dump(exclude_none=True)
        await DAO.add_object(Room, data_dict, db)

    @classmethod
    async def create_booking(cls, booking_data, current_user, db):
        room_exists = await DAO.search_by_fields(
            Room, dict(id=booking_data.room_id), db
        )
        if not room_exists:
            message = "Ошибка. Указанная комната не найдена"
            logger.warning(message)
            raise CredentialsException(status_code=404, detail=message)
        # проверка занятости комнаты на указанные дату и слот
        data_dict = booking_data.model_dump(exclude_none=True)
        existing_booking = await DAO.search_by_fields(Booking, data_dict, db)
        if existing_booking:
            message = "Ошибка. Этот временной слот на выбранную дату уже забронирован"
            logger.warning(message)
            raise CredentialsException(
                status_code=status.HTTP_409_CONFLICT,
                detail=message,
            )

        # создание связи user-room на указанные дату и слот
        data_dict["user_id"] = current_user.id
        new_booking = await DAO.add_object(Booking, data_dict, db)
        return new_booking

    @classmethod
    async def cancel_booking(cls, booking_id, current_user, db):

        booking = await DAO.search_by_fields(Booking, dict(id=booking_id), db)
        if not booking:
            message = "Ошибка. Бронирование не найдено"
            logger.warning(message)
            raise CredentialsException(status_code=404, detail=message)

        if current_user.role != "admin" and booking.user_id != current_user.id:
            message = "Доступ к чужим бронированиям запрещен"
            logger.warning(message)
            raise CredentialsException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=message,
            )

        await DAO.delete_object(booking, db)

    @classmethod
    async def get_available_rooms(cls, booking_date, db):

        if booking_date < date.today():
            message = "Ошибка. Дата не актуальна"
            logger.warning(message)
            raise CredentialsException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message,
            )
        rooms = await DAO.get_rooms_to_date(booking_date, db)
        # список комнат с доступными слотами
        rooms_with_slots = []

        for room in rooms:
            # слоты, которые уже заняты в текущей комнате на указанную дату
            busy_slots = {b.time_slot for b in room.bookings}

            # свободные слоты
            free_slots = [slot for slot in ALLOWED_SLOTS if slot not in busy_slots]
            rooms_with_slots.append(
                {
                    "id": room.id,
                    "name": room.name,
                    "description": room.description,
                    "free_slots": free_slots,
                }
            )

        return rooms_with_slots

    @classmethod
    async def get_my_active_bookings(cls, current_user, db):
        user = await DAO.get_users_with_active_bookings(dict(id=current_user.id), db)
        if user is None:
            return {
                "id": current_user.id,
                "username": current_user.username,
                "name": current_user.name,
                "role": current_user.role,
                "bookings": [],
            }
        return user
