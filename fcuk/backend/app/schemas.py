from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserOut(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    phone: Optional[str]
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    login: str
    password: str

# ────────────────────────────────────────────────
# Заказы
# ────────────────────────────────────────────────

class OrderItemCreate(BaseModel):
    filename: str                    # получено после /upload
    original_name: str
    quantity: int = 1
    filament_type: str
    filament_color: str

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    delivery_method: str
    delivery_address: Optional[str] = None
    comment: Optional[str] = None

class OrderItemOut(BaseModel):
    id: int
    filename: str
    original_name: str
    quantity: int
    filament_type: str
    filament_color: str
    weight_grams: Optional[float] = None
    price_per_item: Optional[float] = None

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    user_id: int
    status: str
    total_price: Optional[float]
    delivery_method: str
    delivery_address: Optional[str]
    comment: Optional[str]
    created_at: datetime
    paid_at: Optional[datetime]
    finished_at: Optional[datetime]
    photos: List[str]
    items: List[OrderItemOut]

    class Config:
        from_attributes = True