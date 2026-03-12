from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_session
from app.models import User
from app.schemas import UserOut

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=list[UserOut])
async def get_all_users(session: AsyncSession = Depends(get_session)):
    stmt = select(User)
    result = await session.execute(stmt)
    users = result.scalars().all()
    return users