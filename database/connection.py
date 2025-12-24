from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
async def initialize_database(self):
    client = AsyncIOMotorClient(self.DATABASE_URL)
    await init_beanie(
    database=client.get_default_database(),
    document_models=[])
class Config:
    env_file = ".env"
'''
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///planner.db"  # Или "sqlite:///database.db" по методичке
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})  # echo=True для логов SQL

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session
'''