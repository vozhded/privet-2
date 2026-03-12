from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload
from typing import List
import os
import uuid
import shutil

from app.database import get_session
from app.models import User, Order, OrderItem
from app.schemas import OrderOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

PHOTO_DIR = "uploads/photos"
os.makedirs(PHOTO_DIR, exist_ok=True)


 #Временно: любой авторизованный пользователь
async def get_any_auth_user(current_user: User = Depends(get_current_user)):
    return current_user


# 1. Все заказы
@router.get("/orders", response_model=List[OrderOut])
async def get_all_orders(
    current_user: User = Depends(get_any_auth_user),
    session: AsyncSession = Depends(get_session)
):
    stmt = (
        select(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.user)
        )
        .order_by(Order.created_at.desc())
    )
    result = await session.execute(stmt)
    orders = result.scalars().all()
    return orders


# 2. Изменение статуса — теперь явно Body()
@router.patch("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    new_status: str = Body(..., embed=True),  # ← КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ
    current_user: User = Depends(get_any_auth_user),
    session: AsyncSession = Depends(get_session)
):
    valid_statuses = ["new", "processing", "printing", "packing", "shipped", "completed", "cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Неверный статус")

    stmt = update(Order).where(Order.id == order_id).values(status=new_status)
    await session.execute(stmt)
    await session.commit()
    return {"message": "Статус обновлён"}


# 3. Загрузка фото
@router.post("/orders/{order_id}/photos")
async def upload_order_photos(
    order_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_any_auth_user),
    session: AsyncSession = Depends(get_session)
):
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    if order.status not in ["packing", "shipped"]:
        raise HTTPException(status_code=400, detail="Фото можно добавлять только на стадии packing/shipped")

    photo_urls = []
    for file in files:
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        path = os.path.join(PHOTO_DIR, filename)
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        photo_urls.append(filename)

    if order.photos:
        order.photos.extend(photo_urls)
    else:
        order.photos = photo_urls

    await session.commit()
    return {"photos_added": photo_urls}


# 4. Дашборд

@router.get("/dashboard")
async def director_dashboard(
    current_user: User = Depends(get_any_auth_user),  # или get_director_user, когда вернёшь роли
    session: AsyncSession = Depends(get_session)
):
    # Все заказы
    all_orders_stmt = select(Order)
    all_orders_result = await session.execute(all_orders_stmt)
    all_orders = all_orders_result.scalars().all()

    # Завершённые
    completed_stmt = select(Order).where(Order.status == "completed")
    completed_result = await session.execute(completed_stmt)
    completed_orders = completed_result.scalars().all()

    # Общая выручка
    total_revenue_stmt = select(func.sum(Order.total_price)).where(Order.total_price.isnot(None))
    total_revenue_result = await session.execute(total_revenue_stmt)
    total_revenue = total_revenue_result.scalar() or 0.0

    # Выручка по завершённым
    completed_revenue_stmt = select(func.sum(Order.total_price)).where(
        Order.status == "completed",
        Order.total_price.isnot(None)
    )
    completed_revenue_result = await session.execute(completed_revenue_stmt)
    completed_revenue = completed_revenue_result.scalar() or 0.0

    return {
        "total_orders": len(all_orders),
        "completed_orders": len(completed_orders),
        "pending_orders": len(all_orders) - len(completed_orders),
        "total_revenue": round(total_revenue, 2),
        "completed_revenue": round(completed_revenue, 2),
        "pending_revenue": round(total_revenue - completed_revenue, 2),
        "message": "Статистика за всё время"
    }