import os
import sys
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

import uvicorn
from asyncpg.exceptions import CannotConnectNowError, UniqueViolationError
from dotenv import find_dotenv, load_dotenv
from fastapi import Depends, FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from sqlalchemy import (
    select,
    update,
)
from sqlalchemy.exc import IntegrityError, ResourceClosedError
from sqlalchemy.ext.asyncio import AsyncSession

from main.schemas import TestSchema
from main.models import User
from main.database import AsyncSessionLocal, Base, engine, session

load_dotenv(find_dotenv())

logger.remove()
format_out = "{module} <green>{time:DD-MM-YYYY HH:mm:ss}</green> {level} <level>{message}</level>"
logger.add(sys.stdout, format=format_out, level="INFO", colorize=True)
logger.level("WARNING", color="<fg 10,190,200>")


status_code_error = 400
token = os.getenv("token")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


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


app = FastAPI(lifespan=lifespan)


@app.get("/api/test", description="Тестовый эндпоинт", response_model=TestSchema)
async def get_user(
    # tg_uid: int = Header(...),
    # authorization_token: str = Header(...),
    session=Depends(get_session),
):
    return {"result": {"message": f"Привет {session=}"}}


if __name__ == "__main__":
    port = 8989
    uvicorn.run("routes:app", port=port)
