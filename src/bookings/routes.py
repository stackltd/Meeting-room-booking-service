import uvicorn
from fastapi import Depends, APIRouter

from src.bookings.schemas import TestSchema
from src.database import get_session


router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("/api/test", description="Тестовый эндпоинт", response_model=TestSchema)
async def get_user(
    # tg_uid: int = Header(...),
    # authorization_token: str = Header(...),
    session=Depends(get_session),
):
    return {"result": {"message": f"Привет {session=}"}}

