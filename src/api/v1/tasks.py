import uuid

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime

from src.core.dependencies.db_dependency import db_manager
from src.schemas.task_schemas import TaskCreate, TaskResponse, TaskStatus, TaskUpdate


router = APIRouter()

@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate = Depends(TaskCreate)):
    ...

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str):
    ...

@router.get("/tasks", response_model=List[TaskResponse])
def get_tasks(status: Optional[TaskStatus] = None):
    ...

@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: str, task_update: TaskUpdate):
    ...

@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str):
    ...