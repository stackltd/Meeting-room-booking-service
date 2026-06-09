import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

from src.auth.dao import AuthDAO
from src.exceptions import CredentialsException

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# указание на URL для аутентификации
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


class AuthService:

    @classmethod
    async def get_user(cls, username, db):
        user = await AuthDAO.search_user(username, db)
        return user

    @classmethod
    async def make_user(cls, user_data, db):
        user_data_dict = user_data.model_dump(exclude_none=True)
        hashed_pwd = AuthService.hash_password(user_data.password)
        user_data_dict.pop("password")
        user_data_dict["password_hash"] = hashed_pwd
        await AuthDAO.add_user(user_data_dict, db)

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
        user = await AuthService.get_user(form_data.username, db)
        if not user or not AuthService.verify_password(
            form_data.password, user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = AuthService.create_access_token(data={"sub": user.username})
        return access_token

    @classmethod
    def get_username_from_token(cls, token: str = Depends(oauth2_scheme)) -> str:
        """Используется для защиты роутов от анонимного доступа. Получение username из JWT-токена."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise CredentialsException()
            return username
        except jwt.PyJWTError:
            raise CredentialsException()
