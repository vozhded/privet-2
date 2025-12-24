from fastapi import FastAPI
from routes.users import router as users_router
from routes.events import router as events_router
from database.connection import init_db

app = FastAPI(title="Planner API by Vazhov Dmitrii")

app.include_router(users_router)
app.include_router(events_router)

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Planner API with MongoDB by Vazhov Dmitrii"}

'''
from fastapi import FastAPI
from routes.users import router as users_router
from routes.events import router as events_router
from database.connection import create_db_and_tables  # Прямой импорт из connection.py

app = FastAPI(title="Planner API by Vazhov Dmitrii")

app.include_router(users_router)
app.include_router(events_router)

create_db_and_tables()  # Вызов для создания БД (как в методичке стр. 3)

@app.get("/")
async def root():
    return {"message": "Planner API with SQL by Vazhov Dmitrii"}


from fastapi import FastAPI
from routes.users import router as users_router
from routes.events import router as events_router

app = FastAPI(title="Planner API by Vazhov Dmitrii")

@app.get("/")
async def root():
    return {"message": "Planner API by Vazhov Dmitrii"}

app.include_router(users_router)    
app.include_router(events_router)
'''
