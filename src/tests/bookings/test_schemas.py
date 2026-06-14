import pytest
from datetime import date, timedelta
from pydantic import ValidationError
from src.bookings.schemas import BookingCreate, RoomBase


def test_booking_date_past():
    """booking_date в прошлом"""
    past_date = date.today() - timedelta(days=1)
    with pytest.raises(ValidationError):
        BookingCreate(room_id=1, booking_date=past_date, time_slot="09:00-11:00")


def test_booking_date_valid():
    """booking_date на сегодняшнюю дату"""
    today = date.today()
    booking = BookingCreate(room_id="10", booking_date=today, time_slot="09:00-11:00")
    assert booking.booking_date == date.today()


def test_booking_time_slot_incorrect():
    """Тайм-слот не в списке ALLOWED_SLOTS"""
    with pytest.raises(ValidationError):
        BookingCreate(room_id=1, booking_date=date.today(), time_slot="09:00-17:00")


def test_booking_time_slot_correct():
    """Тайм-слот в списке ALLOWED_SLOTS"""
    BookingCreate(room_id=1, booking_date=date.today(), time_slot="09:00-11:00")


def test_booking_id_incorrect():
    """Передан некорректный id"""
    with pytest.raises(ValidationError):
        BookingCreate(room_id="1O", booking_date=date.today(), time_slot="09:00-11:00")


def test_create_room_incorrect():
    """Не переданы все требуемые параметры"""
    with pytest.raises(ValidationError):
        RoomBase(description="Комната для 5-7 человек c экраном для презентаций")


def test_create_room_correct():
    """Переданы все требуемые параметры"""
    RoomBase(
        name="Переговорная 6",
    )
