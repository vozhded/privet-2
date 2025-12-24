from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from models.users import User, UserSignIn, UserOut
from database.connection import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserSignIn, session = Depends(get_db)):
    statement = select(User).where(User.email == user_data.email)
    user = session.exec(statement).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(email=user_data.email, password=user_data.password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/login")
async def login(credentials: UserSignIn, session = Depends(get_db)):
    statement = select(User).where(User.email == credentials.email)
    user = session.exec(statement).first()
    if user and user.password == credentials.password:
        return {"message": "Login successful by Vazhov Dmitrii", "user_id": user.id}
    raise HTTPException(status_code=401, detail="Invalid credentials")
'''
from fastapi import APIRouter, HTTPException, status
from models.users import UserSignIn, UserOut

router = APIRouter(prefix="/users", tags=["users"])

users_db: list[dict] = []

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserSignIn):
    if any(u["email"] == user_data.email for u in users_db):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = len(users_db) + 1
    users_db.append({
        "id": user_id,
        "email": user_data.email,
        "password": user_data.password,
        "events": []
    })
    return {"id": user_id, "email": user_data.email}

@router.post("/login")
async def login(credentials: UserSignIn):
    for user in users_db:
        if user["email"] == credentials.email and user["password"] == credentials.password:
            return {"message": "Login successful by Vazhov Dmitrii", "user_id": user["id"]}
    raise HTTPException(status_code=401, detail="Invalid credentials")
'''