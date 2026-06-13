from datetime import date

from pydantic import BaseModel, Field, field_validator

from src.settings import ALLOWED_SLOTS


class RoomBase(BaseModel):
    name: str
    description: str | None = None


class RoomGet(RoomBase):
    id: int

    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    room_id: int
    booking_date: date = Field(description="Дата бронирования в формате YYYY-MM-DD")
    time_slot: str = Field(description="Временной слот формата '09:00-11:00'")

    @field_validator("time_slot")
    @classmethod
    def validate_slot(cls, value: str) -> str:
        if value not in ALLOWED_SLOTS:
            raise ValueError(
                f"Недопустимый временной слот. Доступные: {', '.join(ALLOWED_SLOTS)}"
            )
        return value

    @field_validator("booking_date")
    @classmethod
    def validate_date(cls, value: date) -> date:
        today = date.today()
        if value < today:
            raise ValueError("Нельзя забронировать комнату на прошедшую дату.")
        return value


class UserBookingInUserSchema(BaseModel):
    id: int
    room_id: int
    booking_date: date
    time_slot: str

    class Config:
        from_attributes = True


class UserWithBookingsGet(BaseModel):
    id: int
    username: str
    name: str | None
    role: str
    bookings: list[UserBookingInUserSchema]

    class Config:
        from_attributes = True


class RoomWithFreeSlotsGet(BaseModel):
    id: int
    name: str
    description: str | None = None
    free_slots: list[str]

    class Config:
        from_attributes = True
