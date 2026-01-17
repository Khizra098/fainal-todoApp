"""Todo management endpoints for the Todo Chatbot API."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ...database import get_db
from ...models.task import Task, TaskStatus, TaskPriority
from ...services.task_service import TaskService

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=dict)
def create_todo(
    description: str,
    user_id: int,
    due_date: Optional[datetime] = None,
    category: Optional[str] = None,
    priority: TaskPriority = TaskPriority.medium,
    db: Session = Depends(get_db)
):
    """Create a new todo item."""
    task_service = TaskService(db)
    try:
        task = task_service.add_task(
            description=description,
            user_id=user_id,
            due_date=due_date,
            category=category,
            priority=priority
        )
        return {
            "id": task.id,
            "description": task.description,
            "status": task.status.value,
            "created_date": task.created_date.isoformat() if task.created_date else None,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority.value,
            "user_id": task.user_id
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[dict])
def get_todos(
    user_id: int,
    status: Optional[TaskStatus] = None,
    db: Session = Depends(get_db)
):
    """Get all todos for a specific user with optional status filtering."""
    task_service = TaskService(db)
    tasks = task_service.get_all_tasks(user_id, status)
    return [
        {
            "id": task.id,
            "description": task.description,
            "status": task.status.value,
            "created_date": task.created_date.isoformat() if task.created_date else None,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority.value,
            "user_id": task.user_id
        }
        for task in tasks
    ]


@router.get("/{task_id}", response_model=dict)
def get_todo(
    task_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific todo item."""
    task_service = TaskService(db)
    task = task_service.get_task_by_id(task_id, user_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return {
        "id": task.id,
        "description": task.description,
        "status": task.status.value,
        "created_date": task.created_date.isoformat() if task.created_date else None,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "priority": task.priority.value,
        "user_id": task.user_id
    }


@router.put("/{task_id}/status", response_model=dict)
def update_todo_status(
    task_id: int,
    user_id: int,
    status_update: TaskStatus,
    db: Session = Depends(get_db)
):
    """Update the status of a todo item."""
    task_service = TaskService(db)
    success = task_service.update_task_status(task_id, user_id, status_update)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or not owned by user")

    task = task_service.get_task_by_id(task_id, user_id)
    return {
        "id": task.id,
        "description": task.description,
        "status": task.status.value,
        "updated": True
    }


@router.put("/{task_id}", response_model=dict)
def update_todo(
    task_id: int,
    user_id: int,
    description: Optional[str] = None,
    due_date: Optional[datetime] = None,
    category: Optional[str] = None,
    priority: Optional[TaskPriority] = None,
    db: Session = Depends(get_db)
):
    """Update a todo item's details."""
    task_service = TaskService(db)
    success = task_service.edit_task(
        task_id, user_id,
        description or "",
        due_date,
        category,
        priority
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or not owned by user")

    task = task_service.get_task_by_id(task_id, user_id)
    return {
        "id": task.id,
        "description": task.description,
        "status": task.status.value,
        "created_date": task.created_date.isoformat() if task.created_date else None,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "priority": task.priority.value,
        "user_id": task.user_id
    }


@router.delete("/{task_id}", response_model=dict)
def delete_todo(
    task_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Delete a todo item."""
    task_service = TaskService(db)
    success = task_service.delete_task(task_id, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found or not owned by user")

    return {"success": True, "deleted_task_id": task_id}


@router.post("/search", response_model=List[dict])
def search_todos(
    user_id: int,
    query: str,
    status: Optional[TaskStatus] = None,
    db: Session = Depends(get_db)
):
    """Search for todos by description."""
    task_service = TaskService(db)
    tasks = task_service.search_tasks(user_id, query, status)
    return [
        {
            "id": task.id,
            "description": task.description,
            "status": task.status.value,
            "created_date": task.created_date.isoformat() if task.created_date else None,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "priority": task.priority.value,
            "user_id": task.user_id
        }
        for task in tasks
    ]