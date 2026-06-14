import logging
import time
from contextlib import asynccontextmanager

import uvicorn
from asyncpg.exceptions import CannotConnectNowError
from fastapi import FastAPI

from src.logger import setup_logging
from src.database import engine, session
from src.auth.routes import router as auth_router
from src.bookings.routes import router as bookings_router
from src.users.routes import router as users_router

setup_logging()

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    lifespan
    """
    try:
        logger.info("startup")
        yield
    except (ConnectionRefusedError, ConnectionError, CannotConnectNowError) as ex:
        logger.error(ex)
        logger.info("Ждем завершения инициализации базы данных")
        time.sleep(10)
        yield
    logger.info("Shutdown")
    await session.close()
    await engine.dispose()


app = FastAPI(title="Coworking Booking", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(bookings_router)
app.include_router(users_router)


if __name__ == "__main__":
    # uvicorn src.main:app --reload --port 8989
    port = 8989
    uvicorn.run("main:app", port=port)
