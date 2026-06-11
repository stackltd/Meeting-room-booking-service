from sqlalchemy import select

from src.bookings.models import User


class AuthDAO:
    """Методы для доступа к базе через orm sqlalchemy"""

    @classmethod
    async def search_user(cls, username, db):
        user = await db.execute(select(User).filter_by(username=username))
        user_out = user.scalar_one_or_none()
        return user_out

    @classmethod
    async def add_object(cls, obj, data_dict, db):
        new_obj = obj(**data_dict)
        db.add(new_obj)

    @classmethod
    async def change_object(cls, object, db, data_dict):
        for key, value in data_dict.items():
            setattr(object, key, value)
        db.add(object)
        await db.commit()
