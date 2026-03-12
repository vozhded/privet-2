from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
import os
import uuid
import shutil
from datetime import datetime

from app.database import get_session
from app.models import User, Order, OrderItem
from app.schemas import OrderCreate, OrderOut
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/orders", tags=["orders"])

UPLOAD_DIR = "uploads/models"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ─── 1. Загрузка моделей (теперь несколько файлов) ─────────────────────
@router.post("/upload", response_model=dict)
async def upload_model(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user)
):
    allowed = {'.stl', '.obj', '.3mf'}
    uploaded = []
    for file in files:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in allowed:
            raise HTTPException(400, "Только .stl, .obj, .3mf")

        unique_name = f"{uuid.uuid4()}{ext}"
        path = os.path.join(UPLOAD_DIR, unique_name)

        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        uploaded.append({"filename": unique_name, "original_name": file.filename})

    return {"uploaded": uploaded}


# ─── 2. Создание заказа ──────────────────────────────────────────────
@router.post("/", response_model=OrderOut, status_code=201)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    order = Order(
        user_id=current_user.id,
        status="new",
        delivery_method=order_data.delivery_method,
        delivery_address=order_data.delivery_address,
        comment=order_data.comment
    )
    session.add(order)
    await session.flush()

    for item in order_data.items:
        order_item = OrderItem(
            order_id=order.id,
            filename=item.filename,
            original_name=item.original_name,
            quantity=item.quantity,
            filament_type=item.filament_type,
            filament_color=item.filament_color,
        )
        session.add(order_item)

    order.total_price = 0.0
    await session.commit()
    await session.refresh(order)

    stmt = select(Order).where(Order.id == order.id).options(selectinload(Order.items))
    result = await session.execute(stmt)
    return result.scalar_one()


# ─── 3. Мои заказы ───────────────────────────────────────────────────
@router.get("/my", response_model=List[OrderOut])
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    stmt = (
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .options(selectinload(Order.items))
    )
    result = await session.execute(stmt)
    return result.scalars().all()


# ─── 4. Отмена своего заказа (новый эндпоинт) ────────────────────────
@router.delete("/{order_id}")
async def cancel_my_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    order = await session.get(Order, order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Это не ваш заказ")
    if order.status != "new":
        raise HTTPException(status_code=400, detail="Отменить можно только новые заказы")

    await session.delete(order)
    await session.commit()
    return {"message": "Заказ отменён"}


# ─── 4. Все заказы (для менеджера / директора) ───────────────────────
@router.get("/", response_model=List[OrderOut])
async def get_all_orders(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    if current_user is None or current_user.role not in ("manager", "director"):
        raise HTTPException(403, "Доступ запрещён")

    stmt = (
        select(Order)
        .order_by(Order.created_at.desc())
        .options(selectinload(Order.items), selectinload(Order.user))
    )
    result = await session.execute(stmt)
    return result.scalars().all()


# ─── 5. Изменение статуса заказа (менеджер) ──────────────────────────
@router.patch("/{order_id}/status")
async def update_order_status(
    order_id: int,
    new_status: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    if current_user is None or current_user.role not in ("manager", "director"):
        raise HTTPException(403, "Только менеджер или директор")

    stmt = select(Order).where(Order.id == order_id)
    result = await session.execute(stmt)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(404, "Заказ не найден")

    if new_status not in ["new", "processing", "printing", "packing", "shipped", "completed", "cancelled"]:
        raise HTTPException(400, "Недопустимый статус")

    order.status = new_status
    if new_status == "completed":
        order.finished_at = datetime.utcnow()

    await session.commit()
    return {"message": f"Статус изменён на {new_status}"}