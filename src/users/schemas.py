from pydantic import BaseModel


class UserGet(BaseModel):
    id: int
    username: str
    name: str | None = None
    role: str

    class Config:
        from_attributes = True
