"""
Task model representing a single todo item.
"""

from datetime import datetime
from typing import Optional


class Task:
    """
    Represents a single todo item with attributes ID, description, status, and timestamp.
    """

    def __init__(self, task_id: int, description: str, status: str = "pending", created_date: Optional[datetime] = None):
        """
        Initialize a Task instance.

        Args:
            task_id: Unique identifier for the task
            description: Text content of the task
            status: Status of the task (pending/completed), defaults to "pending"
            created_date: Timestamp when the task was created, defaults to now
        """
        self.id = task_id
        self.description = description
        self.status = status
        self.created_date = created_date if created_date else datetime.now()

    def __str__(self) -> str:
        """
        String representation of the task.

        Returns:
            Formatted string with task details
        """
        return f"[{self.id}] {self.description} ({self.status}) - {self.created_date.strftime('%Y-%m-%d %H:%M:%S')}"

    def to_dict(self) -> dict:
        """
        Convert task to dictionary representation.

        Returns:
            Dictionary with task attributes
        """
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status,
            "created_date": self.created_date.isoformat()
        }