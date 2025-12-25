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
from database.connection import create_db_and_tables 
import uvicorn

app = FastAPI(title="Planner API by Vazhov Dmitrii")

app.include_router(users_router)
app.include_router(events_router)
  
@app.on_event("startup")
async def startup():
    create_db_and_tables()

@app.get("/")
async def root():
    return {"message": "Planner API with SQL by Vazhov Dmitrii"}
    
if __name__ == ' main ':
    uvicorn.run("main:app", host="0.0.0.0", port=8080,reload=True)

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
