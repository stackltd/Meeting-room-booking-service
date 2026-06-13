from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import contains_eager, selectinload

from src.bookings.models import Booking, Room
from src.users.models import User


class DAO:
    """Методы для доступа к базе через orm sqlalchemy"""

    @classmethod
    async def search_by_fields(cls, model, data_dict: dict, db):
        obj = await db.execute(select(model).filter_by(**data_dict))
        return obj.scalar_one_or_none()

    @classmethod
    async def search_all(cls, model, db):
        obj = await db.execute(select(model).order_by(model.id))
        return obj.scalars().all()

    @classmethod
    async def add_object(cls, model, data_dict, db):
        new_obj = model(**data_dict)
        db.add(new_obj)
        await db.commit()

    @classmethod
    async def change_object(cls, obj, db, data_dict):
        for key, value in data_dict.items():
            setattr(obj, key, value)
        db.add(obj)
        await db.commit()

    @classmethod
    async def delete_object(cls, obj, db):
        await db.delete(obj)
        await db.commit()

    @classmethod
    async def get_users_with_active_bookings(cls, db):
        today = date.today()
        query = (
            select(User)
            .join(User.bookings)
            .where(Booking.booking_date >= today)
            # получение в user.bookings результата фильтрации
            .options(contains_eager(User.bookings))
            .order_by(User.id)
        )
        result = await db.execute(query)
        return result.scalars().unique().all()

    @classmethod
    async def get_rooms_to_date(cls, booking_date: date, db):
        # Запрос комнат и бронирований на выбранную дату
        query = select(Room).options(
            selectinload(Room.bookings.and_(Booking.booking_date == booking_date))
        )
        result = await db.execute(query)
        rooms = result.scalars().all()
        return rooms
