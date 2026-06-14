import logging

import pytest
from httpx import AsyncClient

from src.tests.conftest import create_test_user
from src.users.models import User


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    """Создание юзера"""
    response = await client.post(
        "/auth/register",
        json={"username": "test_user", "password": "123456asdZXC*"},
    )

    assert response.status_code == 200
    assert "успешно" in response.text


@pytest.mark.asyncio
async def test_create_double_user(client: AsyncClient, session):
    """Попытка создания дубля юзера"""
    test_user_1 = User(username="test_user", password_hash="...")
    session.add(test_user_1)
    await session.commit()

    response = await client.post(
        "/auth/register",
        json={"username": "test_user", "password": "123456asdZXC*"},
    )

    assert response.status_code == 409
    assert "уже существует" in response.text


@pytest.mark.asyncio
async def test_login(client: AsyncClient, session):
    """Вход в систему"""
    password_plain = "asdZXC123*"
    await create_test_user(password_plain, session)
    response = await client.post(
        "/auth/login",
        data={"username": "test_user", "password": password_plain},
    )
    assert response.status_code == 200
    assert "access_token" in response.text


@pytest.mark.asyncio
async def test_login_with_invalid_password(client: AsyncClient, session):
    """Вход в систему c не верным паролем"""
    password_plain = "asdZXC123*Fh52"
    await create_test_user(password_plain, session)

    response = await client.post(
        "/auth/login",
        data={"username": "test_user", "password": password_plain[1:]},
    )
    assert response.status_code == 401
    assert "Неверный логин или пароль" in response.text


@pytest.mark.asyncio
async def test_change_password(authenticated_client: AsyncClient):
    """Смена пароля"""
    password_plain = "asdZXC123*"
    response = await authenticated_client.patch(
        "/auth/change/password",
        json={"old_password": password_plain, "new_password": "qwerty123ZXC*"},
    )

    assert response.status_code == 200
    assert "успешно изменён" in response.text


@pytest.mark.asyncio
async def test_change_with_incorrect_password(authenticated_client: AsyncClient):
    """Смена пароля при неправильном вводе старого"""
    password_plain = "ZZZppp888*1"
    response = await authenticated_client.patch(
        "/auth/change/password",
        json={"old_password": password_plain, "new_password": "qwerty123ZXC*"},
    )

    assert response.status_code == 401
    assert "Неверный пароль" in response.text


@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_client", ["admin"], indirect=True)
async def test_change_user(authenticated_client: AsyncClient, session):
    """Изменение данных любого пользователя из аккаунта с ролью 'admin'"""
    password_plain = "asdGGG587*"
    await create_test_user(password_plain, session)

    response = await authenticated_client.patch(
        "/auth/change/user",
        json={"username": "test_user", "new_username": "test_user_700"},
    )

    assert response.status_code == 200
    assert "успешно изменил" in response.text


@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_client", ["employee"], indirect=True)
async def test_change_user_with_role_employee(
    authenticated_client: AsyncClient, session
):
    """Попытка доступа к эндпоинту, требующему права админа из аккаунта с ролью 'employee'"""
    response = await authenticated_client.patch(
        "/auth/change/user",
        json={"username": "test_user", "new_username": "test_user_700"},
    )

    assert response.status_code == 401
