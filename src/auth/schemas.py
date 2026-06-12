from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str | None = Field(default=None, min_length=4)
    name: str | None = Field(default=None, description="Имя пользователя")


class UserCreate(UserBase):
    username: str = Field(default="login", min_length=4)
    password: str = Field(
        default="password", min_length=8, description="Пароль пользователя"
    )


class PasswordChange(BaseModel):
    old_password: str = Field(
        default="old_password", min_length=8, description="Старый пароль"
    )
    new_password: str = Field(
        default="new_password", min_length=8, description="Новый пароль"
    )


class UserUpdate(UserBase):
    password: str | None = Field(default=None, min_length=8, description="Новый пароль")
    role: str | None = Field(default=None, description="Смена роли пользователя")
    new_username: str | None = Field(
        default=None, min_length=4, description="Новый логин"
    )
