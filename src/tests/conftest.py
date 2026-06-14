import logging
from datetime import date

import bcrypt
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.bookings.models import Room, Booking
from src.dependencies import get_session, get_current_user, get_admin
from src.main import app
from src.database import Base
from src.users.models import User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(
    engine_test, expire_on_commit=False, class_=AsyncSession
)


@pytest_asyncio.fixture(autouse=True, scope="function")
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session():
    """Фикстура для получения сессии БД внутри тестов"""
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    """Фикстура подмены БД на тестовую"""

    async def _get_test_db():
        async with async_session_maker() as session:
            yield session

    # подмена get_session на тестовую базу
    app.dependency_overrides[get_session] = _get_test_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    # Очищаем подмену после теста
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def authenticated_client(client, request):
    # Создание мок-асинхронной функции, которая возвращает юзера
    role = getattr(request, "param", "employee")

    async def _get_mock_user():
        return User(
            id=1,
            username=f"test_{role}",
            role=role,
            # хеш для пароля asdZXC123*
            password_hash="$2b$12$/rLQHt7asFSbC84cead0m.jcQz8kRnBfNwUiqqmKAKjfWH5pze9Sa",
        )

    # Переопределение зависимости авторизации в FastAPI:
    if role == "admin":
        app.dependency_overrides[get_admin] = _get_mock_user
        app.dependency_overrides[get_current_user] = _get_mock_user
    else:
        app.dependency_overrides[get_current_user] = _get_mock_user

    # проброс фейк-токена в клиент для OAuth2PasswordBearer/HTTPBearer для /login
    client.headers.update({"Authorization": "Bearer fake-mock-token"})

    yield client

    # удаление зависимости и заголовков по завершению теста
    app.dependency_overrides.clear()
    if "Authorization" in client.headers:
        del client.headers["Authorization"]


async def create_test_user(password_plain, session):
    password_bytes = password_plain.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode("utf-8")
    test_user = User(
        username="test_user", password_hash=hashed_password, role="employee"
    )
    session.add(test_user)
    await session.commit()
    await session.flush()
    return test_user


async def cancel_booking(session, user_id):
    test_room = Room(id=1, name="Переговорная 5")
    session.add(test_room)
    await session.flush()
    # создаем второго юзера только для тестирования возможности удалять чужие брони
    if user_id == 2:
        await create_test_user(password_plain="asadPPP25*", session=session)

    test_booking = Booking(
        room_id=1,
        user_id=user_id,
        booking_date=date(2028, 6, 18),
        time_slot="09:00-11:00",
    )
    session.add(test_booking)
    await session.commit()
    return test_booking
