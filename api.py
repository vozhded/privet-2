from fastapi import FastAPI
from todo import todo_router

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Vazhov Dmitrii"}

app.include_router(todo_router)
