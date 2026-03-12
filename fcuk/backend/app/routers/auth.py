from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy import select, or_  
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel 
from app.database import get_session
from app.models import User
from app.schemas import UserCreate, UserOut, Token, LoginRequest
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    login: str        # сюда можно передать либо email, либо username
    password: str
    
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    # Проверка уникальности email
    email_stmt = select(User).where(User.email == user_data.email)
    result = await session.execute(email_stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован"
        )

    # Проверка уникальности username
    username_stmt = select(User).where(User.username == user_data.username)
    result = await session.execute(username_stmt)
    if result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такой username уже занят"
        )

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        role="client"
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

@router.post("/create-manager", status_code=201)
async def create_manager(session: AsyncSession = Depends(get_session)):
    hashed = get_password_hash("123")
    user = User(
        email="manager@example.com",
        username="manager",
        hashed_password=hashed,
        full_name="Менеджер",
        phone="+79991234567",
        role="director"
    )
    session.add(user)
    await session.commit()
    return {"message": "Менеджер создан, логин: manager / пароль: manager123"}

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    # Ищем пользователя по email или username (form_data.username)
    statement = select(User).where(
        or_(
            User.email == form_data.username,
            User.username == form_data.username
        )
    )
    result = await session.execute(statement)
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/me", response_model=UserOut)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
   return current_user