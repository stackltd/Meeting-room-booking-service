from datetime import date

from pydantic import BaseModel, Field, field_validator, ConfigDict

from src.settings import ALLOWED_SLOTS


class RoomBase(BaseModel):
    name: str
    description: str | None = None


class RoomGet(RoomBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


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
    model_config = ConfigDict(from_attributes=True)

    id: int
    room_id: int
    booking_date: date
    time_slot: str


class UserWithBookingsGet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    name: str | None
    role: str
    bookings: list[UserBookingInUserSchema]


class RoomWithFreeSlotsGet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    free_slots: list[str]
