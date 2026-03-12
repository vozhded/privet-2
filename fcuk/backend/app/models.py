# app/models.py
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy.types import JSON

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None  # для доставки
    role: str = Field(default="client")  # client, manager, packer, director
    created_at: datetime = Field(default_factory=datetime.utcnow)

    orders: List["Order"] = Relationship(back_populates="user")


class OrderItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    filename: str                     # имя файла на сервере (например, uuid.stl)
    original_name: str                # оригинальное имя от пользователя
    quantity: int = Field(default=1, ge=1)
    filament_type: str                # PLA, ABS, PETG, Resin и т.д.
    filament_color: str               # "Красный", "#FF0000", "Чёрный" и т.д.
    weight_grams: Optional[float] = Field(default=None, ge=0)
    price_per_item: Optional[float] = Field(default=None, ge=0)

    order: "Order" = Relationship(back_populates="items")


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    
    status: str = Field(default="new")  # new, processing, printing, packing, shipped, completed, cancelled
    total_price: Optional[float] = Field(default=None, ge=0)
    delivery_method: str                 # pickup, courier, post, etc.
    delivery_address: Optional[str] = None
    comment: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    paid_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    
    # Поле для фотографий упаковки (список путей или URL)
    photos: List[str] = Field(
        default_factory=list,
        sa_type=JSON, sa_column_kwargs={"default": []}
    )

    user: User = Relationship(back_populates="orders")
    items: List[OrderItem] = Relationship(back_populates="order", cascade_delete=True)