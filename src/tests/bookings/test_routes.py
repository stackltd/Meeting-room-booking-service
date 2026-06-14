from datetime import date

import pytest
from httpx import AsyncClient

from src.bookings.models import Room, Booking


@pytest.mark.asyncio
async def test_create_booking(authenticated_client_employee: AsyncClient, session):
    #  Создание комнаты с id=1 в тестовой БД
    test_room = Room(id=1, name="Переговорная 5")
    session.add(test_room)
    await session.commit()

    response = await authenticated_client_employee.post(
        "/bookings",
        json={"room_id": 1, "booking_date": "2026-06-15", "time_slot": "09:00-11:00"},
    )

    assert response.status_code == 200
    assert "забронирована" in response.text


@pytest.mark.asyncio
async def test_create_double_booking(
    authenticated_client_employee: AsyncClient, session
):
    #  Создание комнаты в тестовой БД
    test_room = Room(id=1, name="Переговорная 5")
    session.add(test_room)

    # первое бронирование напрямую
    existing_booking = Booking(
        room_id=1, user_id=1, booking_date=date(2026, 6, 18), time_slot="09:00-11:00"
    )
    session.add(existing_booking)
    await session.commit()

    # Второе бронирование на те же данные через url
    response = await authenticated_client_employee.post(
        "/bookings",
        json={"room_id": 1, "booking_date": "2026-06-18", "time_slot": "09:00-11:00"},
    )

    assert response.status_code == 409
    assert "уже забронирован" in response.text
