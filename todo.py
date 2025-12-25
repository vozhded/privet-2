'''
from fastapi import APIRouter, Path
from model import Todo  

todo_router = APIRouter()

todo_list = [Todo(id=1, item="Example_Schema")]

@todo_router.post("/todo")
async def add_todo(todo: Todo) -> dict:
    todo_list.append(todo)
    return {"message": "Задача добавлена успешно!"}  

@todo_router.get("/todo")
async def retrieve_todos() -> dict:
    return {"todos": todo_list}

@todo_router.get("/todo/{todo_id}")
async def get_single_todo(todo_id: int = Path(..., title="ID задачи для получения")) -> dict:
    for todo in todo_list:
        if todo.id == todo_id:
            return {"todo": todo}
    return {"message": "Задача с указанным ID не существует!"}
'''
'''
from fastapi import APIRouter, Path, HTTPException, status
from model import Todo, TodoItem, TodoItems

todo_router = APIRouter()

todo_list = [Todo(id=1, item="Example_Schema")]

@todo_router.post("/todo", status_code=status.HTTP_201_CREATED)
async def add_todo(todo: Todo) -> dict:
    todo_list.append(todo)
    return {"message": "Задача добавлена успешно by Vazhov Dmitrii!"}

@todo_router.get("/todo", response_model=TodoItems)
async def retrieve_todos() -> dict:
    return {"todos": todo_list}

@todo_router.get("/todo/{todo_id}")
async def get_single_todo(todo_id: int = Path(..., title="ID задачи для получения")) -> dict:
    for todo in todo_list:
        if todo.id == todo_id:
            return {"todo": todo}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача с указанным ID не существует!")

@todo_router.put("/todo/{todo_id}")
async def update_todo(todo_data: TodoItem, todo_id: int = Path(..., title="ID задачи для обновления")) -> dict:
    for todo in todo_list:
        if todo.id == todo_id:
            todo.item = todo_data.item
            return {"message": "Задача обновлена успешно by Vazhov Dmitrii!"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача с указанным ID не существует!")

@todo_router.delete("/todo/{todo_id}")
async def delete_single_todo(todo_id: int = Path(..., title="ID задачи для удаления")) -> dict:
    for index in range(len(todo_list)):
        if todo_list[index].id == todo_id:
            todo_list.pop(index)
            return {"message": "Задача удалена успешно by Vazhov Dmitrii!"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача с указанным ID не существует!")

@todo_router.delete("/todo")
async def delete_all_todos() -> dict:
    todo_list.clear()
    return {"message": "Все задачи удалены успешно by Vazhov Dmitrii!"}
'''
from fastapi import APIRouter, Path, HTTPException, status
from model import Todo, TodoItem, TodoItems

todo_router = APIRouter()

todo_list = []

@todo_router.post("/todo", status_code=status.HTTP_201_CREATED)
async def add_todo(todo: Todo) -> dict:
    todo.id = len(todo_list) + 1
    todo_list.append(todo)
    return {"message": "Задача добавлена успешно by Vazhov Dmitrii!"}

@todo_router.get("/todo", response_model=TodoItems)
async def retrieve_todos() -> dict:
    return {"todos": todo_list}

@todo_router.get("/todos", response_model=TodoItems)
async def retrieve_todos_alt() -> dict:
    return {"todos": todo_list}

@todo_router.get("/todo/{todo_id}", response_model=Todo)
async def get_single_todo(todo_id: int = Path(..., title="ID задачи для получения")) -> dict:
    for todo in todo_list:
        if todo.id == todo_id:
            return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача с указанным ID не существует!")

@todo_router.put("/todo/{todo_id}")
async def update_todo(todo_data: TodoItem, todo_id: int = Path(..., title="ID задачи для обновления")) -> dict:
    for todo in todo_list:
        if todo.id == todo_id:
            todo.item = todo_data.item
            return {"message": "Задача обновлена успешно by Vazhov Dmitrii!"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача с указанным ID не существует!")

@todo_router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_todo(todo_id: int = Path(..., title="ID задачи для удаления")):
    for index in range(len(todo_list)):
        if todo_list[index].id == todo_id:
            todo_list.pop(index)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача с указанным ID не существует!")

@todo_router.delete("/todo", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_todos():
    todo_list.clear()
    return