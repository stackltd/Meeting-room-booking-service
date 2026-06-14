import pytest
from httpx import AsyncClient

from src.users.models import User


@pytest.mark.asyncio
async def test_get_my_profile_success(authenticated_client: AsyncClient, session):
    """Пользователь получает свой профиль"""
    test_user = User(
        id=1, username="test_employee", role="employee", password_hash="..."
    )
    session.add(test_user)
    await session.commit()

    response = await authenticated_client.get("/users/me")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "test_employee"
    assert "password_hash" not in data


@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_client", ["admin"], indirect=True)
async def test_get_any_user_profile_as_admin(
    authenticated_client: AsyncClient, session
):
    """Админ может найти любого пользователя по его username"""
    # Создаем админа в БД
    admin_user = User(id=1, username="test_admin", role="admin", password_hash="...")
    # Создаем пользователя, которого админ будет искать
    target_user = User(id=2, username="someone", role="employee", password_hash="...")

    session.add_all([admin_user, target_user])
    await session.commit()
    # Делаем запрос по username целевого пользователя
    response = await authenticated_client.get("/users/someone")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 2
    assert data["username"] == "someone"


@pytest.mark.asyncio
async def test_get_any_user_profile_forbidden_for_employee(
    authenticated_client: AsyncClient, session
):
    """Обычный сотрудник не имеет права искать пользователей по username"""
    target_user = User(id=2, username="someone", role="employee", password_hash="...")
    session.add(target_user)
    await session.commit()

    response = await authenticated_client.get("/users/someone")

    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize("authenticated_client", ["admin"], indirect=True)
async def test_get_all_users_as_admin(authenticated_client: AsyncClient, session):
    """Админ получает список всех пользователей"""
    user_admin = User(id=1, username="admin_user", role="admin", password_hash="...")
    user_1 = User(id=2, username="user_1", role="employee", password_hash="...")
    user_2 = User(id=3, username="user_2", role="employee", password_hash="...")

    session.add_all([user_admin, user_1, user_2])
    await session.commit()

    response = await authenticated_client.get("/users")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]["username"] == "admin_user"
    assert data[1]["username"] == "user_1"
    assert data[2]["username"] == "user_2"


@pytest.mark.asyncio
async def test_get_all_users_forbidden_for_employee(authenticated_client: AsyncClient):
    """Обычный сотрудник не может получить список всех пользователей (401/403)"""
    response = await authenticated_client.get("/users")

    assert response.status_code in [401, 403]
