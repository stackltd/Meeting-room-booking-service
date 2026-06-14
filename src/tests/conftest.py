import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.dependencies import get_session, get_current_user
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
async def authenticated_client_employee(client, session):
    # Создание мок-асинхронной функции, которая возвращает юзера
    async def _get_mock_employee():
        return User(id=1, username="test_user", role="employee", password_hash="...")

    # Переопределение зависимости авторизации в FastAPI
    app.dependency_overrides[get_current_user] = _get_mock_employee

    yield client


# @pytest_asyncio.fixture
# async def authenticated_client_employee(client, session):
#     # Создание мок-асинхронной функции, которая возвращает юзера
#     async def _get_mock_employee():
#         return User(
#             id=1,
#             username="test_user",
#             role="employee",
#             password_hash="..."
#         )
#
#     # Переопределение зависимости авторизации в FastAPI
#     app.dependency_overrides[get_current_user] = _get_mock_employee
#
#     yield client
