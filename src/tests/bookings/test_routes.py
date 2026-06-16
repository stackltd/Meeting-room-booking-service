from datetime import date, timedelta

import pytest
from httpx import AsyncClient

from src.bookings.models import Room, Booking
from src.tests.conftest import create_test_user, cancel_booking

# Календарные даты для тестов активных/неактивных бронирований
TODAY = date.today()
TOMORROW = TODAY + timedelta(days=1)
YESTERDAY = TODAY - timedelta(days=1)


@pytest.mark.asyncio
async def test_create_booking(authenticated_client: AsyncClient, session):
    """Создание комнаты с id=1 в тестовой БД"""
    test_room = Room(id=1, name="Переговорная 5")
    session.add(test_room)
    await session.commit()

    response = await authenticated_client.post(
        "/bookings",
        json={"room_id": 1, "booking_date": "2028-06-15", "time_slot": "09:00-11:00"},
    )

    assert response.status_code == 200
    assert "забронирована" in response.text


@pytest.mark.asyncio
async def test_create_double_booking(authenticated_client: AsyncClient, session):
    """Создание комнаты в тестовой БД"""
    test_room = Room(id=1, name="Переговорная 5")
    session.add(test_room)

    # первое бронирование напрямую
    existing_booking = Booking(
        room_id=1, user_id=1, booking_date=date(2028, 6, 18), time_slot="09:00-11:00"
    )
    session.add(existing_booking)
    await session.commit()

    # Второе бронирование на те же данные через url
    response = await authenticated_client.post(
        "/bookings",
        json={"room_id": 1, "booking_date": "2028-06-18", "time_slot": "09:00-11:00"},
    )

    assert response.status_code == 409
    assert "уже забронирован" in response.text


@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_client", ["employee"], indirect=True)
async def test_cancel_booking(authenticated_client: AsyncClient, session):
    """Отмена своего бронирования"""
    test_booking = await cancel_booking(session, user_id=1)

    response = await authenticated_client.delete(f"/bookings/{test_booking.id}")
    assert response.status_code == 200
    assert "успешно отменено" in response.text


@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_client", ["admin"], indirect=True)
async def test_cancel_someone_booking(authenticated_client: AsyncClient, session):
    """Отмена чужого бронирования"""
    test_booking = await cancel_booking(session, user_id=2)
    response = await authenticated_client.delete(f"/bookings/{test_booking.id}")

    assert response.status_code == 200
    assert "успешно отменено" in response.text


@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_client", ["employee"], indirect=True)
async def test_cancel_someone_booking_as_employee(
    authenticated_client: AsyncClient, session
):
    """Попытка отмены чужого бронирования под аккаунтом employee"""
    test_booking = await cancel_booking(session, user_id=2)
    response = await authenticated_client.delete(f"/bookings/{test_booking.id}")

    assert response.status_code == 403
    assert "запрещен" in response.text


@pytest.mark.asyncio
async def test_get_rooms_success(client: AsyncClient, session):
    """Проверка получения списка всех комнат (доступно без авторизации)"""
    room_1 = Room(id=1, name="Малая переговорная")
    room_2 = Room(id=2, name="Большой конференц-зал")
    session.add_all([room_1, room_2])
    await session.commit()

    response = await client.get("/bookings/rooms")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["name"] == "Малая переговорная"
    assert data[1]["name"] == "Большой конференц-зал"


@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_client", ["admin"], indirect=True)
async def test_get_active_users_as_admin(authenticated_client: AsyncClient, session):
    """Админ видит список пользователей с активными бронями"""
    await create_test_user("asdPPP123*", session)

    room = Room(id=1, name="Переговорная 1")
    booking = Booking(
        room_id=1, user_id=1, booking_date=TOMORROW, time_slot="09:00-11:00"
    )
    session.add_all([room, booking])
    await session.commit()

    response = await authenticated_client.get("/bookings/users-current-bookings")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == 1
    assert len(data[0]["bookings"]) == 1
    assert data[0]["bookings"][0]["time_slot"] == "09:00-11:00"


@pytest.mark.asyncio
async def test_get_active_users_forbidden_for_employee(
    authenticated_client: AsyncClient,
):
    """Попытка доступа обычного сотрудника к эндпоинту админа"""
    response = await authenticated_client.get("/bookings/users-current-bookings")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_my_active_bookings(authenticated_client: AsyncClient, session):
    """Обычный пользователь получает информацию о себе и только СВОИХ активных бронях"""
    await create_test_user("asdPPP123*", session)

    room = Room(id=1, name="Переговорная 1")

    # Бронь созданного пользователя (user_id=1 из create_test_user) на завтра
    my_active_booking = Booking(
        room_id=1, user_id=1, booking_date=TOMORROW, time_slot="09:00-11:00"
    )

    # Бронь текущего пользователя, но вчерашняя
    my_past_booking = Booking(
        room_id=1, user_id=1, booking_date=YESTERDAY, time_slot="13:00-15:00"
    )

    # Чужая активная бронь (user_id=99)
    someone_booking = Booking(
        room_id=1, user_id=99, booking_date=TOMORROW, time_slot="17:00-19:00"
    )

    session.add_all([room, my_active_booking, my_past_booking, someone_booking])
    await session.commit()

    response = await authenticated_client.get("/bookings/me")

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == 1
    assert "password_hash" not in data  # проверка оптимизации бд

    # Проверка возврата одной активной брони пользователя
    assert len(data["bookings"]) == 1
    assert data["bookings"][0]["time_slot"] == "09:00-11:00"
    assert data["bookings"][0]["booking_date"] == str(TOMORROW)


@pytest.mark.asyncio
async def test_get_available_rooms(client: AsyncClient, session):
    """Проверка фильтрации свободных комнат на указанную дату"""

    room_1 = Room(id=1, name="Свободная комната")
    room_2 = Room(id=2, name="Частично занятая комната")

    booking = Booking(
        room_id=2, user_id=1, booking_date=TOMORROW, time_slot="11:00-13:00"
    )

    session.add_all([room_1, room_2, booking])
    await session.commit()

    response = await client.get(f"/bookings/room-available?booking_date={TOMORROW}")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2  # Должны вернуться обе комнаты, но у одной слот занят
    # поиск данных комнаты 2 и отсутствия там слота "11:00-13:00"
    for room in data:
        if room["id"] == 2:
            data = room
            break
    assert "11:00-13:00" not in data
