"""待办事项 API：演示工程（初始状态，/healthz 将由流水线生成）"""
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Todo API", version="0.1.0")

_todos: List[dict] = []


class TodoIn(BaseModel):
    title: str
    done: bool = False


class Todo(TodoIn):
    id: str
    created_at: str


@app.get("/todos", response_model=List[Todo])
def list_todos(sort: Optional[str] = None):
    """列出所有待办。sort=created_at:desc 时按创建时间降序。"""
    items = _todos
    if sort == "created_at:desc":
        items = sorted(_todos, key=lambda t: t["created_at"], reverse=True)
    return items


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(payload: TodoIn):
    todo = {
        "id": str(uuid4()),
        "title": payload.title,
        "done": payload.done,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _todos.append(todo)
    return todo


@app.patch("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: str, payload: TodoIn):
    for t in _todos:
        if t["id"] == todo_id:
            t.update(payload.model_dump())
            return t
    raise HTTPException(status_code=404, detail="todo not found")


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: str):
    global _todos
    _todos = [t for t in _todos if t["id"] != todo_id]
