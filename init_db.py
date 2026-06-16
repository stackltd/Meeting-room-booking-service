import asyncio
import logging
from datetime import date, timedelta
from sqlalchemy import select
from src.database import AsyncSessionLocal, engine
from src.users.models import User
from src.bookings.models import Booking
from src.bookings.models import Room
from src.auth.service import AuthService


logger = logging.getLogger("app")


async def seed_data():
    """Создание тестовых пользователй, комнат и бронирований при старте контейнера"""

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalars().first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=AuthService.hash_password("admin123"),
                role="admin",
            )
            session.add(admin)

        result = await session.execute(select(User).where(User.username == "employee"))
        employee = result.scalars().first()

        if not employee:
            employee = User(
                username="employee",
                password_hash=AuthService.hash_password("employee123"),
                role="employee",
            )
            session.add(employee)

        result = await session.execute(select(Room))
        rooms = result.scalars().all()

        if not rooms:
            room1 = Room(name="Большая переговорная")
            room2 = Room(name="Малая переговорная")
            session.add_all([room1, room2])
            await session.flush()
        else:
            room1, room2 = rooms[0], rooms[1] if len(rooms) > 1 else rooms[0]

        result = await session.execute(select(Booking))
        bookings = result.scalars().all()

        if not bookings:
            await session.flush()

            booking1 = Booking(
                user_id=employee.id,
                room_id=room1.id,
                booking_date=date.today(),
                time_slot="13:00-15:00",
            )
            booking2 = Booking(
                user_id=admin.id,
                room_id=room2.id,
                booking_date=date.today() + timedelta(days=1),
                time_slot="15:00-17:00",
            )
            session.add_all([booking1, booking2])

        await session.commit()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_data())
    logger.info("Data seeding completed!")
