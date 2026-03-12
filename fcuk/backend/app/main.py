from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ← Новый импорт
from app.database import init_db
from app.routers.auth import router as auth_router
from app.routers.orders import router as orders_router
from app.routers.admin import router as admin_router
from app.routers.users import router as users_router
from fastapi.staticfiles import StaticFiles
import os


app = FastAPI(title="3D Print Platform", version="1.0")



# ==================== CORS ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене замени на твой домен, пока "*" для разработки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === СТАТИКА ДЛЯ ФОТО И МОДЕЛЕЙ ===
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ==================== Роутеры ====================
app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(admin_router)
app.include_router(users_router)


@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/")
async def root():
    return {"message": "3D Print Platform API работает!"}


