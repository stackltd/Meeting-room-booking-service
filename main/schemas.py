from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class TestSchema(BaseModel):
    result: Dict[str, str] = Field(
        {}, description="Тестовое сообщение"
    )
