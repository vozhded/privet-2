from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime

if TYPE_CHECKING:
    from .users import User  # Для Pylance, чтобы не ругался на цикл

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    image: str  # Из методички
    description: str  # Из методички
    tags: List[str] = Field(sa_column=Column(JSON))  # Из методички, как JSON
    location: str  # Из методички
    date_time: datetime  # Ваше дополнение
    owner_id: int = Field(foreign_key="user.id")  # Ваше дополнение

    owner: Optional["User"] = Relationship(back_populates="events")  # Обратная связь

    class Config:
        arbitrary_types_allowed = True  # Для JSON
        json_schema_extra = {
            "example": {
                "title": "FastAPI Book Launch",
                "image": "https://linktomyimage.com/image.png",
                "description": "We will be discussing the contents of the FastAPI book in this event. Ensure to come with your own copy to win gifts!",
                "tags": ["python", "fastapi", "book", "launch"],
                "location": "Google Meet",
                "date_time": "2025-11-05T10:00:00"
            }
        }

class EventUpdate(SQLModel):  # Из методички для частичных обновлений
    title: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    location: Optional[str] = None
    date_time: Optional[datetime] = None  # Ваше дополнение

    class Config:
        json_schema_extra = {
            "example": {
                "title": "FastAPI Book Launch",
                "image": "https://linktomyimage.com/image.png",
                "description": "We will be discussing the contents of the FastAPI book in this event. Ensure to come with your own copy to win gifts!",
                "tags": ["python", "fastapi", "book", "launch"],
                "location": "Google Meet",
                "date_time": "2025-11-05T10:00:00"
            }
        }
'''
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Event(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    date_time: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Team Meeting",
                "description": "Weekly sync",
                "date_time": "2025-11-05T10:00:00"
            }
        }
'''