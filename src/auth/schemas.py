import re

from pydantic import BaseModel, Field, field_validator


def check_password(value):
    # Требование минимум 1 заглавную букву, 1 строчную, 1 цифру и 1 спецсимвол
    password_regex = re.compile(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,}$"
    )

    if not password_regex.match(value):
        raise ValueError(
            "Пароль должен быть не менее 8 символов и содержать "
            "хотя бы одну заглавную букву, одну строчную букву, "
            "одну цифру и один специальный символ (@$!%*?&_)."
        )
    return value


class UserBase(BaseModel):
    username: str | None = Field(default=None, min_length=4)
    name: str | None = Field(default=None, description="Имя пользователя")


class UserCreate(UserBase):
    username: str = Field(default="login", min_length=4)
    password: str = Field(
        default="password", min_length=8, description="Пароль пользователя"
    )

    @field_validator("password")
    @classmethod
    def validate_date(cls, value):
        return check_password(value)


class PasswordChange(BaseModel):
    old_password: str = Field(
        default="old_password", min_length=8, description="Старый пароль"
    )
    new_password: str = Field(
        default="new_password", min_length=8, description="Новый пароль"
    )

    @field_validator("new_password")
    @classmethod
    def validate_date(cls, value):
        return check_password(value)


class UserUpdate(UserBase):
    password: str | None = Field(default=None, min_length=8, description="Новый пароль")
    role: str | None = Field(default=None, description="Смена роли пользователя")
    new_username: str | None = Field(
        default=None, min_length=4, description="Новый логин"
    )
