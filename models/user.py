from beanie import Document
from pydantic import EmailStr
from typing import List

class User(Document):
    email: EmailStr
    password: str
    events: List[dict] = []

    class Settings:
        name = "users"

class UserSignIn(User):
    pass

class UserOut(User):
    id: str

'''
from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from .events import Event  # Для Pylance, чтобы не ругался на цикл

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(index=True)
    password: str  # В реальности хэшируйте!

    events: List["Event"] = Relationship(back_populates="owner")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "fastapi@packt.com",
                "password": "strong!!!"
            }
        }

class UserSignIn(SQLModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "fastapi@packt.com",
                "password": "strong!!!"
            }
        }

class UserOut(SQLModel):
    id: int
    email: EmailStr



from pydantic import BaseModel, EmailStr
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "fastapi@packt.com",
                "password": "strong!!!"
            }
        }

class UserSignIn(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "fastapi@packt.com",
                "password": "strong!!!"
            }
        }

class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "fastapi@packt.com"
            }
        }
'''