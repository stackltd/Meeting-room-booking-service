from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(default="login", min_length=3)
    password: str = Field(
        default="password", min_length=8, description="Пароль пользователя"
    )
    name: str | None = Field(default=None, description="your_name")
