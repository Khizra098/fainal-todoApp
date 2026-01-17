"""Task service for managing todo tasks with database operations."""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from ..models.task import Task, TaskStatus, TaskPriority


class TaskService:
    """
    Service class for managing task operations (CRUD functionality) with database persistence.
    """

    def __init__(self, db: Session):
        """
        Initialize the TaskService with a database session.

        Args:
            db: Database session for operations
        """
        self.db = db

    def add_task(self, description: str, user_id: int, due_date: Optional[datetime] = None,
                 category: Optional[str] = None, priority: TaskPriority = TaskPriority.medium) -> Task:
        """
        Add a new task to the database.

        Args:
            description: Description of the task to add
            user_id: ID of the user who owns this task
            due_date: Optional due date for the task
            category: Optional category for the task
            priority: Priority level of the task (default: medium)

        Returns:
            The newly created Task object

        Raises:
            ValueError: If description is empty or None
        """
        if not description or not description.strip():
            raise ValueError("Task description cannot be empty")

        task = Task(
            description=description.strip(),
            user_id=user_id,
            due_date=due_date,
            category=category,
            priority=priority
        )

        try:
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            return task
        except IntegrityError:
            self.db.rollback()
            raise ValueError(f"Failed to create task for user {user_id}")

    def get_all_tasks(self, user_id: int, status: Optional[TaskStatus] = None) -> List[Task]:
        """
        Get all tasks for a specific user with optional status filtering.

        Args:
            user_id: ID of the user whose tasks to retrieve
            status: Optional status to filter tasks by

        Returns:
            List of Task objects for the user
        """
        query = self.db.query(Task).filter(Task.user_id == user_id)

        if status:
            query = query.filter(Task.status == status)

        return query.all()

    def get_task_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        """
        Get a specific task by its ID for a specific user.

        Args:
            task_id: ID of the task to retrieve
            user_id: ID of the user who owns the task

        Returns:
            Task object if found and belongs to user, None otherwise
        """
        return self.db.query(Task).filter(Task.id == task_id, Task.user_id == user_id).first()

    def update_task_status(self, task_id: int, user_id: int, status: TaskStatus) -> bool:
        """
        Update the status of a task.

        Args:
            task_id: ID of the task to update
            user_id: ID of the user who owns the task
            status: New status for the task

        Returns:
            True if the task was updated, False if not found or not owned by user
        """
        task = self.get_task_by_id(task_id, user_id)
        if task:
            task.status = status
            self.db.commit()
            self.db.refresh(task)
            return True
        return False

    def edit_task(self, task_id: int, user_id: int, new_description: str,
                  new_due_date: Optional[datetime] = None, new_category: Optional[str] = None,
                  new_priority: Optional[TaskPriority] = None) -> bool:
        """
        Edit the description and other properties of a task.

        Args:
            task_id: ID of the task to edit
            user_id: ID of the user who owns the task
            new_description: New description for the task
            new_due_date: New due date for the task (optional)
            new_category: New category for the task (optional)
            new_priority: New priority for the task (optional)

        Returns:
            True if the task was updated, False if not found or not owned by user
        """
        if not new_description or not new_description.strip():
            raise ValueError("Task description cannot be empty")

        task = self.get_task_by_id(task_id, user_id)
        if task:
            task.description = new_description.strip()
            if new_due_date is not None:
                task.due_date = new_due_date
            if new_category is not None:
                task.category = new_category
            if new_priority is not None:
                task.priority = new_priority

            self.db.commit()
            self.db.refresh(task)
            return True
        return False

    def delete_task(self, task_id: int, user_id: int) -> bool:
        """
        Delete a task by its ID for a specific user.

        Args:
            task_id: ID of the task to delete
            user_id: ID of the user who owns the task

        Returns:
            True if the task was deleted, False if not found or not owned by user
        """
        task = self.get_task_by_id(task_id, user_id)
        if task:
            self.db.delete(task)
            self.db.commit()
            return True
        return False

    def complete_task(self, task_id: int, user_id: int) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: ID of the task to mark as completed
            user_id: ID of the user who owns the task

        Returns:
            True if the task was marked as completed, False if not found or not owned by user
        """
        return self.update_task_status(task_id, user_id, TaskStatus.completed)

    def search_tasks(self, user_id: int, query: str, status: Optional[TaskStatus] = None) -> List[Task]:
        """
        Search for tasks by description containing the query string.

        Args:
            user_id: ID of the user whose tasks to search
            query: Query string to search for in task descriptions
            status: Optional status to filter results by

        Returns:
            List of Task objects matching the search criteria
        """
        query_filter = f"%{query}%"
        db_query = self.db.query(Task).filter(
            Task.user_id == user_id,
            Task.description.ilike(query_filter)
        )

        if status:
            db_query = db_query.filter(Task.status == status)

        return db_query.all()