from pydantic import BaseModel, Field


class UserGet(BaseModel):
    id: int
    username: str
    name: str | None = None
    role: str

    # интеграция с SQLAlchemy
    class Config:
        from_attributes = True


class RoomBase(BaseModel):
    name: str
    description: str | None = None


class RoomGet(RoomBase):
    id: int

    class Config:
        from_attributes = True
