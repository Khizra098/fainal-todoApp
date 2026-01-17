"""MCP (Model Context Protocol) tool endpoints for the Todo Chatbot API."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from ...database import get_db
from ...services.mcp_tool_service import MCPToolService


router = APIRouter(prefix="/mcp", tags=["mcp"])


class CreateTodoRequest(BaseModel):
    description: str
    due_date: Optional[str] = None
    priority: str = "medium"


class UpdateTodoStatusRequest(BaseModel):
    task_id: int
    status: str


class DeleteTodoRequest(BaseModel):
    task_id: int


class SearchTodosRequest(BaseModel):
    query: str
    status: Optional[str] = None


class ListTodosRequest(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    limit: Optional[int] = None


class SetReminderRequest(BaseModel):
    task_id: Optional[int] = None
    description: Optional[str] = None
    remind_at: str


@router.post("/create_todo")
def create_todo_mcp(
    request: CreateTodoRequest,
    user_id: int,
    db: Session = Depends(get_db)
):
    """MCP tool endpoint to create a new todo item."""
    mcp_service = MCPToolService(db)

    # Convert due_date string to datetime if provided
    due_date = None
    if request.due_date:
        try:
            due_date = datetime.fromisoformat(request.due_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid due_date format. Use ISO 8601 format."
            )

    result = mcp_service.create_todo(
        user_id=user_id,
        description=request.description,
        due_date=due_date,
        priority=request.priority
    )

    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    return result


@router.post("/list_todos")
def list_todos_mcp(
    request: ListTodosRequest,
    user_id: int,
    db: Session = Depends(get_db)
):
    """MCP tool endpoint to retrieve a list of todo items with optional filtering."""
    mcp_service = MCPToolService(db)

    result = mcp_service.list_todos(
        user_id=user_id,
        status=request.status,
        priority=request.priority,
        limit=request.limit
    )

    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    return result


@router.post("/update_todo_status")
def update_todo_status_mcp(
    request: UpdateTodoStatusRequest,
    user_id: int,
    db: Session = Depends(get_db)
):
    """MCP tool endpoint to update the status of a specific todo item."""
    mcp_service = MCPToolService(db)

    result = mcp_service.update_todo_status(
        user_id=user_id,
        task_id=request.task_id,
        status=request.status
    )

    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    return result


@router.post("/delete_todo")
def delete_todo_mcp(
    request: DeleteTodoRequest,
    user_id: int,
    db: Session = Depends(get_db)
):
    """MCP tool endpoint to remove a specific todo item."""
    mcp_service = MCPToolService(db)

    result = mcp_service.delete_todo(
        user_id=user_id,
        task_id=request.task_id
    )

    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    return result


@router.post("/search_todos")
def search_todos_mcp(
    request: SearchTodosRequest,
    user_id: int,
    db: Session = Depends(get_db)
):
    """MCP tool endpoint to search for todos by description or other criteria."""
    mcp_service = MCPToolService(db)

    result = mcp_service.search_todos(
        user_id=user_id,
        query=request.query,
        status=request.status
    )

    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    return result


@router.post("/set_reminder")
def set_reminder_mcp(
    request: SetReminderRequest,
    user_id: int,
    db: Session = Depends(get_db)
):
    """MCP tool endpoint to set a reminder for a specific task or event."""
    mcp_service = MCPToolService(db)

    # Convert remind_at string to datetime
    try:
        remind_at = datetime.fromisoformat(request.remind_at.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid remind_at format. Use ISO 8601 format."
        )

    result = mcp_service.set_reminder(
        user_id=user_id,
        task_id=request.task_id,
        description=request.description,
        remind_at=remind_at
    )

    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    return result