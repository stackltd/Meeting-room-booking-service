from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import HTTPException, status

from src.bookings.service import BookingsService
from src.dao import DAO
from src.bookings.models import User
from src.dependencies import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from src.exceptions import CredentialsException


class AuthService:

    @classmethod
    async def make_user(cls, user_data, db):
        user_data_dict = user_data.model_dump(exclude_none=True)
        hashed_pwd = cls.hash_password(user_data.password)
        user_data_dict.pop("password")
        user_data_dict["password_hash"] = hashed_pwd
        await DAO.add_object(User, user_data_dict, db)

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Хеширование пароля"""
        password_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        # Хеширование пароля с добавленной "солью" и сохранения в БД в виде строки
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        return hashed_password.decode("utf-8")

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """Проверка соответствия чистого пароля и хеша из БД."""
        password_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    @classmethod
    def create_access_token(cls, data: dict) -> str:
        """Генерация JWT-токена со сроком действия."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @classmethod
    async def make_token(cls, form_data, db):

        # проверка существования пользователя с username
        user = await DAO.search_by_field(User, dict(username=form_data.username), db)
        if not user or not cls.verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # создание токена с зашитым в него username и фрагмента хеша пароля
        access_token = cls.create_access_token(
            data={"sub": user.username, "pwd_version": user.password_hash[:10]}
        )
        return access_token

    @classmethod
    async def change_password(cls, passwords, current_user, db):
        if not cls.verify_password(passwords.old_password, current_user.password_hash):
            raise CredentialsException(detail="Неверный пароль")

        hashed_pwd = cls.hash_password(passwords.new_password)
        data_for_change = dict(password_hash=hashed_pwd)
        await DAO.change_object(current_user, db, data_for_change)

    @classmethod
    async def change_user(cls, user_data, db):
        username = user_data.username
        user = await DAO.search_by_field(User, dict(username=username), db)
        if not user:
            raise CredentialsException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пользователь {username} не найден",
            )
        data_dict = user_data.model_dump(exclude_unset=True)
        if user_data.password:
            hashed_pwd = cls.hash_password(user_data.password)
            data_dict.pop("password")
            data_dict["password_hash"] = hashed_pwd
        if user_data.new_username:
            data_dict.pop("new_username")
            data_dict["username"] = user_data.new_username
        await DAO.change_object(user, db, data_dict)
