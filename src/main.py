import sys
import time
from contextlib import asynccontextmanager

import uvicorn
from asyncpg.exceptions import CannotConnectNowError
from fastapi import FastAPI
from loguru import logger


logger.remove()
format_out = "{module} <green>{time:DD-MM-YYYY HH:mm:ss}</green> {level} <level>{message}</level>"
logger.add(sys.stdout, format=format_out, level="INFO", colorize=True)
logger.level("WARNING", color="<fg 10,190,200>")


from src.database import engine, session
# from src.auth.router import router as auth_router
from src.bookings.routes import router as bookings_router

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
        logger.info("Ждем окончания инициализации базы данных")
        time.sleep(10)
        yield
    logger.info("Shutdown")
    await session.close()
    await engine.dispose()




app = FastAPI(title="Coworking Booking", lifespan=lifespan)

# app.include_router(auth_router)
app.include_router(bookings_router)


if __name__ == "__main__":
    port = 8989
    uvicorn.run("main:app", port=port)
