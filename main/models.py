from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, Integer, BigInteger, DateTime, String
from sqlalchemy.dialects.postgresql import JSONB

from database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(20), default="employee")

    def __getitem__(self, point):
        return getattr(self, point)

    def to_json(self) -> Dict[str, Any]:
        result_json = {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name != "id"
        }
        return {"user": result_json, "result": True}
