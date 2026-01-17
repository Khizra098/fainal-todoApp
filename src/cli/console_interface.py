"""
Console interface for the Todo application.
"""

import sys
from typing import List
from ..models.task import Task
from ..services.task_service import TaskService


class ConsoleInterface:
    """
    Console interface for user interaction with the todo application.
    """

    def __init__(self, task_service: TaskService):
        """
        Initialize the console interface with a task service.

        Args:
            task_service: Instance of TaskService to manage tasks
        """
        self.task_service = task_service

    def display_help(self):
        """
        Display help information with all available commands.
        """
        print("\nAvailable commands:")
        print("  add <description>    - Add a new task")
        print("  list                 - List all tasks")
        print("  complete <id>        - Mark a task as completed")
        print("  edit <id> <new_desc> - Edit a task description")
        print("  delete <id>          - Delete a task")
        print("  help                 - Show this help message")
        print("  quit                 - Exit the application")
        print()

    def display_tasks(self, tasks: List[Task]):
        """
        Display a list of tasks in a formatted way.

        Args:
            tasks: List of Task objects to display
        """
        if not tasks:
            print("\nNo tasks in your list.")
            return

        print("\nYour tasks:")
        print("-" * 60)
        for task in tasks:
            status_symbol = "✓" if task.status == "completed" else "○"
            print(f"{status_symbol} {task}")
        print("-" * 60)

    def parse_command(self, user_input: str) -> tuple:
        """
        Parse user command input into command and arguments.

        Args:
            user_input: Raw input from user

        Returns:
            Tuple of (command, arguments list)
        """
        parts = user_input.strip().split()
        if not parts:
            return "", []

        command = parts[0].lower()
        args = parts[1:]

        return command, args

    def handle_add_command(self, args: List[str]) -> bool:
        """
        Handle the 'add' command to create a new task.

        Args:
            args: Arguments for the add command (task description)

        Returns:
            True if successful, False otherwise
        """
        if len(args) == 0:
            print("Error: Please provide a task description. Usage: add <description>")
            return False

        description = " ".join(args)
        try:
            task = self.task_service.add_task(description)
            print(f"Task added successfully: {task}")
            return True
        except ValueError as e:
            print(f"Error: {e}")
            return False

    def handle_list_command(self, args: List[str]) -> bool:
        """
        Handle the 'list' command to display all tasks.

        Args:
            args: Arguments for the list command (ignored)

        Returns:
            True if successful, False otherwise
        """
        if args:
            print("Warning: 'list' command doesn't take any arguments")

        tasks = self.task_service.get_all_tasks()
        self.display_tasks(tasks)
        return True

    def handle_complete_command(self, args: List[str]) -> bool:
        """
        Handle the 'complete' command to mark a task as completed.

        Args:
            args: Arguments for the complete command (task ID)

        Returns:
            True if successful, False otherwise
        """
        if len(args) != 1:
            print("Error: Please provide a task ID. Usage: complete <id>")
            return False

        try:
            task_id = int(args[0])
            success = self.task_service.complete_task(task_id)
            if success:
                print(f"Task {task_id} marked as completed.")
            else:
                print(f"Error: Task with ID {task_id} not found.")
            return success
        except ValueError:
            print("Error: Task ID must be a number.")
            return False

    def handle_edit_command(self, args: List[str]) -> bool:
        """
        Handle the 'edit' command to update a task description.

        Args:
            args: Arguments for the edit command (task ID and new description)

        Returns:
            True if successful, False otherwise
        """
        if len(args) < 2:
            print("Error: Please provide task ID and new description. Usage: edit <id> <new_desc>")
            return False

        try:
            task_id = int(args[0])
            new_description = " ".join(args[1:])
            success = self.task_service.edit_task(task_id, new_description)
            if success:
                print(f"Task {task_id} updated successfully.")
            else:
                print(f"Error: Task with ID {task_id} not found.")
            return success
        except ValueError as e:
            print(f"Error: {e}")
            return False

    def handle_delete_command(self, args: List[str]) -> bool:
        """
        Handle the 'delete' command to remove a task.

        Args:
            args: Arguments for the delete command (task ID)

        Returns:
            True if successful, False otherwise
        """
        if len(args) != 1:
            print("Error: Please provide a task ID. Usage: delete <id>")
            return False

        try:
            task_id = int(args[0])
            success = self.task_service.delete_task(task_id)
            if success:
                print(f"Task {task_id} deleted successfully.")
            else:
                print(f"Error: Task with ID {task_id} not found.")
            return success
        except ValueError:
            print("Error: Task ID must be a number.")
            return False

    def handle_help_command(self, args: List[str]) -> bool:
        """
        Handle the 'help' command to show available commands.

        Args:
            args: Arguments for the help command (ignored)

        Returns:
            True if successful, False otherwise
        """
        if args:
            print("Warning: 'help' command doesn't take any arguments")

        self.display_help()
        return True

    def handle_quit_command(self, args: List[str]) -> bool:
        """
        Handle the 'quit' command to exit the application.

        Args:
            args: Arguments for the quit command (ignored)

        Returns:
            True if successful, False otherwise
        """
        if args:
            print("Warning: 'quit' command doesn't take any arguments")

        print("Exiting the application. Goodbye!")
        return True

    def handle_invalid_command(self, command: str) -> bool:
        """
        Handle invalid commands.

        Args:
            command: The unrecognized command

        Returns:
            False to indicate failure
        """
        print(f"Error: Unknown command '{command}'. Type 'help' for available commands.")
        return False

    def run_command(self, command: str, args: List[str]) -> bool:
        """
        Execute a parsed command with its arguments.

        Args:
            command: The command to execute
            args: Arguments for the command

        Returns:
            True if command executed successfully, False otherwise
        """
        command_handlers = {
            'add': self.handle_add_command,
            'list': self.handle_list_command,
            'complete': self.handle_complete_command,
            'edit': self.handle_edit_command,
            'delete': self.handle_delete_command,
            'help': self.handle_help_command,
            'quit': self.handle_quit_command,
            'exit': self.handle_quit_command,  # Alternative to quit
        }

        handler = command_handlers.get(command)
        if handler:
            return handler(args)
        else:
            return self.handle_invalid_command(command)

    def start_interactive_mode(self):
        """
        Start the interactive console interface.
        """
        print("Welcome to the Todo Console Application!")
        print("Type 'help' for available commands or 'quit' to exit.\n")

        while True:
            try:
                user_input = input("todo> ").strip()

                if not user_input:
                    continue

                command, args = self.parse_command(user_input)

                if command in ['quit', 'exit']:
                    self.handle_quit_command(args)
                    break

                self.run_command(command, args)

            except KeyboardInterrupt:
                print("\n\nExiting the application. Goodbye!")
                break
            except EOFError:
                print("\n\nExiting the application. Goodbye!")
                break