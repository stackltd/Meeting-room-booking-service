from sqlalchemy import select

from src.bookings.models import User


class AuthDAO:
    """Методы для доступа к базе через orm sqlalchemy"""

    @classmethod
    async def search_user(cls, username, db):
        user = await db.execute(select(User).filter_by(username=username))
        user_exist = user.scalar_one_or_none()
        return user_exist

    @classmethod
    async def add_user(cls, user_data_dict, db):
        new_user = User(**user_data_dict)
        db.add(new_user)
