"""MCP Tool service for managing MCP tool operations."""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import json
from ..models.task import Task, TaskStatus, TaskPriority, Conversation, Message, RoleType
from .task_service import TaskService
from .conversation_service import ConversationService


class MCPToolService:
    """
    Service class for managing MCP tool operations and interactions.
    """

    def __init__(self, db: Session):
        """
        Initialize the MCPToolService with a database session.

        Args:
            db: Database session for operations
        """
        self.db = db
        self.task_service = TaskService(db)
        self.conversation_service = ConversationService(db)

    def create_todo(self, user_id: int, description: str, due_date: Optional[datetime] = None,
                    priority: str = "medium") -> Dict[str, Any]:
        """
        Create a new todo item via MCP tool.

        Args:
            user_id: ID of the user creating the task
            description: Description of the task to create
            due_date: Optional due date for the task
            priority: Priority level ('low', 'medium', 'high')

        Returns:
            Dictionary with success status and task information
        """
        try:
            # Validate priority
            priority_enum = TaskPriority(priority.lower())

            task = self.task_service.add_task(
                description=description,
                user_id=user_id,
                due_date=due_date,
                priority=priority_enum
            )

            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "description": task.description,
                    "status": task.status.value,
                    "created_date": task.created_date.isoformat() if task.created_date else None,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority.value
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def list_todos(self, user_id: int, status: Optional[str] = None,
                   priority: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Retrieve a list of todo items with optional filtering via MCP tool.

        Args:
            user_id: ID of the user whose tasks to retrieve
            status: Optional status to filter by ('pending', 'completed', 'in-progress')
            priority: Optional priority to filter by ('low', 'medium', 'high')
            limit: Optional maximum number of tasks to return

        Returns:
            Dictionary with success status and list of tasks
        """
        try:
            # Get all tasks for the user
            tasks = self.task_service.get_all_tasks(user_id)

            # Apply status filter if provided
            if status:
                status_enum = TaskStatus(status.lower())
                tasks = [task for task in tasks if task.status == status_enum]

            # Apply priority filter if provided
            if priority:
                priority_enum = TaskPriority(priority.lower())
                tasks = [task for task in tasks if task.priority == priority_enum]

            # Apply limit if provided
            if limit:
                tasks = tasks[:limit]

            # Format tasks for response
            formatted_tasks = []
            for task in tasks:
                formatted_tasks.append({
                    "id": task.id,
                    "description": task.description,
                    "status": task.status.value,
                    "created_date": task.created_date.isoformat() if task.created_date else None,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority.value
                })

            return {
                "success": True,
                "tasks": formatted_tasks
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def update_todo_status(self, user_id: int, task_id: int, status: str) -> Dict[str, Any]:
        """
        Update the status of a specific todo item via MCP tool.

        Args:
            user_id: ID of the user who owns the task
            task_id: ID of the task to update
            status: New status for the task ('pending', 'completed', 'in-progress')

        Returns:
            Dictionary with success status and updated task information
        """
        try:
            # Validate status
            status_enum = TaskStatus(status.lower())

            success = self.task_service.update_task_status(task_id, user_id, status_enum)

            if success:
                task = self.task_service.get_task_by_id(task_id, user_id)
                return {
                    "success": True,
                    "task": {
                        "id": task.id,
                        "description": task.description,
                        "status": task.status.value,
                        "updated": True
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Task with ID {task_id} not found or not owned by user"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def delete_todo(self, user_id: int, task_id: int) -> Dict[str, Any]:
        """
        Delete a specific todo item via MCP tool.

        Args:
            user_id: ID of the user who owns the task
            task_id: ID of the task to delete

        Returns:
            Dictionary with success status and deleted task ID
        """
        try:
            success = self.task_service.delete_task(task_id, user_id)

            if success:
                return {
                    "success": True,
                    "deleted_task_id": task_id
                }
            else:
                return {
                    "success": False,
                    "error": f"Task with ID {task_id} not found or not owned by user"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def search_todos(self, user_id: int, query: str, status: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for todos by description or other criteria via MCP tool.

        Args:
            user_id: ID of the user whose tasks to search
            query: Search query string
            status: Optional status to filter by ('pending', 'completed', 'in-progress')

        Returns:
            Dictionary with success status and list of matching tasks
        """
        try:
            # Validate status if provided
            status_enum = None
            if status:
                status_enum = TaskStatus(status.lower())

            tasks = self.task_service.search_tasks(user_id, query, status_enum)

            # Format tasks for response
            formatted_tasks = []
            for task in tasks:
                formatted_tasks.append({
                    "id": task.id,
                    "description": task.description,
                    "status": task.status.value,
                    "created_date": task.created_date.isoformat() if task.created_date else None,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "priority": task.priority.value
                })

            return {
                "success": True,
                "tasks": formatted_tasks
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def set_reminder(self, user_id: int, task_id: Optional[int] = None, description: Optional[str] = None,
                     remind_at: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Set a reminder for a specific task or event via MCP tool.

        Args:
            user_id: ID of the user setting the reminder
            task_id: Optional ID of the task to set reminder for
            description: Description of the reminder (required if task_id not provided)
            remind_at: When to send the reminder (required)

        Returns:
            Dictionary with success status and reminder information
        """
        try:
            if not remind_at:
                return {
                    "success": False,
                    "error": "remind_at is required"
                }

            # In a real implementation, this would create a reminder in a separate table
            # For now, we'll just return a mock reminder response
            reminder_data = {
                "id": 1,  # Mock ID
                "description": description or f"Reminder for task {task_id}" if task_id else "General reminder",
                "remind_at": remind_at.isoformat() if remind_at else None,
                "created_at": datetime.utcnow().isoformat(),
                "task_id": task_id
            }

            return {
                "success": True,
                "reminder": reminder_data
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }