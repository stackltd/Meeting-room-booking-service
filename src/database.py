import os

from dotenv import find_dotenv, load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv(find_dotenv())

login = os.getenv("db_login")
password = os.getenv("db_password")
name = os.getenv("db_name")

# для подключения к контейнеру с postgres, но через приложение снаружи
DATABASE_URL = f"postgresql+asyncpg://{login}:{password}@localhost:5433/{name}"

# использовать для сборки контейнера с приложением fastapi
# DATABASE_URL = f"postgresql+asyncpg://{login}:{password}@postgres:5432/{name}"


engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
session = AsyncSessionLocal()


class Base(DeclarativeBase):
    pass
