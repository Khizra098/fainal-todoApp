"""
Task service for managing todo tasks.
"""

from typing import List, Optional
from ..models.task import Task


class TaskService:
    """
    Service class for managing task operations (CRUD functionality).
    """

    def __init__(self):
        """
        Initialize the TaskService with an empty in-memory storage.
        """
        self._tasks: List[Task] = []
        self._next_id = 1

    def add_task(self, description: str) -> Task:
        """
        Add a new task to the task list.

        Args:
            description: Description of the task to add

        Returns:
            The newly created Task object

        Raises:
            ValueError: If description is empty or None
        """
        if not description or not description.strip():
            raise ValueError("Task description cannot be empty")

        task = Task(
            task_id=self._next_id,
            description=description.strip()
        )
        self._tasks.append(task)
        self._next_id += 1
        return task

    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks in the task list.

        Returns:
            List of all Task objects
        """
        return self._tasks.copy()

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Get a specific task by its ID.

        Args:
            task_id: ID of the task to retrieve

        Returns:
            Task object if found, None otherwise
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None

    def update_task_status(self, task_id: int, status: str) -> bool:
        """
        Update the status of a task.

        Args:
            task_id: ID of the task to update
            status: New status for the task (should be 'pending' or 'completed')

        Returns:
            True if the task was updated, False if not found
        """
        if status not in ["pending", "completed"]:
            raise ValueError(f"Invalid status: {status}. Status must be 'pending' or 'completed'.")

        task = self.get_task_by_id(task_id)
        if task:
            task.status = status
            return True
        return False

    def edit_task(self, task_id: int, new_description: str) -> bool:
        """
        Edit the description of a task.

        Args:
            task_id: ID of the task to edit
            new_description: New description for the task

        Returns:
            True if the task was updated, False if not found
        """
        if not new_description or not new_description.strip():
            raise ValueError("Task description cannot be empty")

        task = self.get_task_by_id(task_id)
        if task:
            task.description = new_description.strip()
            return True
        return False

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if the task was deleted, False if not found
        """
        task = self.get_task_by_id(task_id)
        if task:
            self._tasks.remove(task)
            return True
        return False

    def complete_task(self, task_id: int) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: ID of the task to mark as completed

        Returns:
            True if the task was marked as completed, False if not found
        """
        return self.update_task_status(task_id, "completed")

    def get_next_id(self) -> int:
        """
        Get the next available task ID.

        Returns:
            The next available ID for a new task
        """
        return self._next_id