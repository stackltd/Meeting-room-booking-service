import pytest
from pydantic import ValidationError

from src.auth.schemas import UserCreate, PasswordChange


def test_create_user():
    """Регистрация пользователя"""
    UserCreate(username="superuser", password="qweASD123*")


def test_create_user_with_incorrect_username():
    """Некорректное поле username"""
    with pytest.raises(ValidationError):
        UserCreate(username="asd", password="12345678*aB")


def test_create_user_with_incorrect_password():
    """Некорректное поле password"""
    with pytest.raises(ValidationError):
        UserCreate(username="superuser", password="1234567D")


def test_change_password():
    """Смена пароля"""
    PasswordChange(old_password="Superuser12*", new_password="qweASD123*")


def test_change_with_incorrect_password():
    """Неудачная попытка смены пароля"""
    with pytest.raises(ValidationError):
        PasswordChange(old_password="Superuser12*", new_password="123456asdP")
