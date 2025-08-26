import uuid
import datetime

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional


from src.core.dependencies.db_dependency import db_manager
from src.schemas.task_schemas import TaskCreate, TaskResponse, TaskStatus, TaskUpdate, TaskID


router = APIRouter()

@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(task_data: TaskCreate = Depends(TaskCreate)) -> TaskResponse:
    task_id = str(uuid.uuid4())
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    with db_manager.get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (id, title, description, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (task_id, task_data.title, task_data.description, task_data.status.value, now, now)
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        created_task = cursor.fetchone()
        
        if not created_task:
            raise HTTPException(
                status_code=500,
                detail="Ошибка при создании задачи"
                )
            
        return {
            'id': created_task[0],
            'title': created_task[1],
            'description': created_task[2],
            'status': created_task[3],
            'created_at': created_task[4],
            'updated_at': created_task[5],
        }

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_one_task(task_id: TaskID = Depends(TaskID)) -> TaskResponse:
    with db_manager.get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id.id,))
        task = cursor.fetchone()
        
        if not task:
            raise HTTPException(
                status_code=404, 
                detail="Задача не найдена"\
                )
            
        return {
            'id': task[0],
            'title': task[1],
            'description': task[2],
            'status': task[3],
            'created_at': task[4],
            'updated_at': task[5],
        }

@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(status: Optional[TaskStatus] = None) -> List[TaskResponse]:
    with db_manager.get_conn() as conn:
        cursor = conn.cursor()
        
        if status:
            cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC", (status.value,))
        else:
            cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            
        tasks = cursor.fetchall()
        return [
                {
                    'id': task[0],
                    'title': task[1],
                    'description': task[2],
                    'status': task[3],
                    'created_at': task[4],
                    'updated_at': task[5],
                } for task in tasks
            ]
    
@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_update: TaskUpdate = Depends(TaskUpdate)) -> TaskResponse:
    with db_manager.get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_update.id,))
        existing_task = cursor.fetchone()
        
        if not existing_task:
            raise HTTPException(
                status_code=404,
                detail="Задача не найдена"
                )
        
        update_fields = {}
        if task_update.title is not None:
            update_fields['title'] = task_update.title
        if task_update.description is not None:
            update_fields['description'] = task_update.description
        if task_update.status is not None:
            update_fields['status'] = task_update.status.value
        
        if not update_fields:
            raise HTTPException(
                status_code=400,
                detail="Нет параметров для обновления"
                )
        
        set_clause = ", ".join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values())
        values.append(datetime.datetime.now(datetime.timezone.utc).isoformat())
        values.append(task_update.id)
        
        cursor.execute(
            f"UPDATE tasks SET {set_clause}, updated_at = ? WHERE id = ?",
            values
        )
        conn.commit()
        
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_update.id,))
        updated_task = cursor.fetchone()
        
        return {
            'id': updated_task[0],
            'title': updated_task[1],
            'description': updated_task[2],
            'status': updated_task[3],
            'created_at': updated_task[4],
            'updated_at': updated_task[5],
        }

@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: str):
    with db_manager.get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Задача не найдена"
                )
            
        conn.commit()
        return None