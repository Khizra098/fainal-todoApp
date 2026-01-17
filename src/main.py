"""
Main entry point for the Todo Console Application.
"""

from .services.task_service import TaskService
from .cli.console_interface import ConsoleInterface


def main():
    """
    Main function to run the Todo Console Application.
    """
    # Initialize the task service
    task_service = TaskService()

    # Initialize the console interface
    console_interface = ConsoleInterface(task_service)

    # Start the interactive mode
    console_interface.start_interactive_mode()


if __name__ == "__main__":
    main()