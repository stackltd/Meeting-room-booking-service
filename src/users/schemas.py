from pydantic import BaseModel, ConfigDict


class UserGet(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    name: str | None = None
    role: str
