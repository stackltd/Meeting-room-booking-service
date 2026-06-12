from sqlalchemy import select

from src.bookings.models import User, Room


class DAO:
    """Методы для доступа к базе через orm sqlalchemy"""

    @classmethod
    async def search_by_field(cls, model, data_dict, db):
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
    async def change_object(cls, model, db, data_dict):
        for key, value in data_dict.items():
            setattr(model, key, value)
        db.add(model)
        await db.commit()
