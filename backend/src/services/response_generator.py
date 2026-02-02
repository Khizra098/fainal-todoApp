"""
Response generator service for the AI Assistant Chat feature.
This module generates appropriate responses based on message type and content.
"""

import random
from typing import Optional, Dict, List
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """
    Service class to generate appropriate responses based on message type and content.
    """

    def __init__(self):
        # Task-related response templates
        self.task_templates = {
            "add_task": [
                "To add a new task, simply type your task in the input field and press Enter or click the '+' button.",
                "You can create a new task by entering it in the text box and submitting it.",
                "Just type what you need to do and hit the add button to create a new task.",
                "Enter your task in the input field and click the 'Add Task' button to save it."
            ],
            "complete_task": [
                "To mark a task as complete, click the checkbox next to the task.",
                "Simply click the circle icon next to the task to mark it as done.",
                "Check the box beside the task to mark it as completed.",
                "Click on the task's checkbox to indicate it's finished."
            ],
            "delete_task": [
                "To delete a task, click the trash icon next to the task.",
                "Remove a task by clicking the delete button associated with it.",
                "Swipe left or click the delete icon to remove a task.",
                "Find the task and click the 'X' button to delete it."
            ],
            "general_task_help": [
                "I can help you manage your tasks. You can ask me to add, complete, or delete tasks.",
                "Feel free to ask about adding tasks, marking them complete, or organizing your list.",
                "I'm here to assist with your task management. What would you like to do?",
                "You can manage your tasks by adding new ones, completing existing ones, or removing unwanted tasks."
            ]
        }

        # Greeting response templates
        self.greeting_templates = [
            "Hello! How can I help you with your tasks today?",
            "Hi there! Need assistance with managing your tasks?",
            "Greetings! What can I do to help with your task management?",
            "Hey! How can I assist you with your tasks?",
            "Hello! I'm here to help you manage your tasks efficiently.",
            "Hi! Feel free to ask me about adding, completing, or organizing your tasks.",
            "Welcome! I'm your AI assistant for task management. How can I help?",
            "Good day! I'm here to assist with your task management needs.",
            "Hello there! Ready to tackle some tasks? How can I help?",
            "Hi! I'm your task management assistant. What would you like to do?",
            "Greetings! I'm here to make task management easier for you."
        ]

        # Non-task response templates
        self.non_task_templates = [
            "Task-related input required.",
            "I'm designed to help with task management. Please keep your questions related to tasks and productivity.",
            "I'm focused on helping you manage your tasks. For other questions, please consult an appropriate resource.",
            "My purpose is to assist with task management. I can help you add, complete, or organize your tasks.",
            "I'm here to help with task-related queries. For other topics, please seek elsewhere.",
            "I can only assist with task management. Please keep your questions focused on tasks and productivity.",
            "I'm here to help you manage your tasks. Please stick to task-related queries.",
            "For the best experience, please ask questions related to task management."
        ]

    def generate_response(self, user_message: str, message_type: str, context: Optional[Dict] = None) -> str:
        """
        Generate an appropriate response based on the user message and its classification.

        Args:
            user_message (str): The original message from the user
            message_type (str): The type of message ('task_related', 'greeting', 'non_task')
            context (Optional[Dict]): Additional context for the conversation

        Returns:
            str: The generated response
        """
        logger.debug(f"Generating response for message type: {message_type}, message: '{user_message[:50]}...'")

        if message_type == "greeting":
            response = self._generate_greeting_response(user_message)
        elif message_type == "task_related":
            response = self._generate_task_response(user_message)
        elif message_type == "non_task":
            response = self._generate_non_task_response(user_message)
        else:
            # Default to general help if message type is unknown
            response = random.choice(self.task_templates["general_task_help"])

        logger.debug(f"Generated response: '{response[:50]}...'")
        return response

    def _generate_greeting_response(self, user_message: str) -> str:
        """
        Generate a greeting response.

        Args:
            user_message (str): The user's greeting message

        Returns:
            str: A greeting response
        """
        return random.choice(self.greeting_templates)

    def _generate_task_response(self, user_message: str) -> str:
        """
        Generate a task-related response based on the specific task query.

        Args:
            user_message (str): The user's task-related message

        Returns:
            str: A task-related response
        """
        user_message_lower = user_message.lower()

        # Determine the specific type of task query
        if any(word in user_message_lower for word in ["add", "create", "new", "make", "+"]):
            return random.choice(self.task_templates["add_task"])
        elif any(word in user_message_lower for word in ["complete", "done", "finish", "completed", "check", "tick", "mark"]):
            return random.choice(self.task_templates["complete_task"])
        elif any(word in user_message_lower for word in ["delete", "remove", "trash", "x", "cancel", "eliminate"]):
            return random.choice(self.task_templates["delete_task"])
        else:
            # For general task queries, provide general help
            return random.choice(self.task_templates["general_task_help"])

    def _generate_non_task_response(self, user_message: str) -> str:
        """
        Generate a response for non-task-related messages.

        Args:
            user_message (str): The user's non-task-related message

        Returns:
            str: A response directing back to task management
        """
        return random.choice(self.non_task_templates)

    def generate_contextual_response(self, user_message: str, message_type: str, conversation_context: List[Dict]) -> str:
        """
        Generate a response that takes into account the conversation history.

        Args:
            user_message (str): The current user message
            message_type (str): The type of message
            conversation_context (List[Dict]): Previous messages in the conversation

        Returns:
            str: A contextual response
        """
        # For now, we'll use the standard response generator
        # In a more advanced implementation, this could use the context
        # to provide more personalized responses
        return self.generate_response(user_message, message_type)

    def get_response_tone(self, message_type: str) -> str:
        """
        Get the appropriate tone for the response based on message type.

        Args:
            message_type (str): The type of message

        Returns:
            str: The appropriate tone ('friendly', 'helpful', 'professional', etc.)
        """
        if message_type == "greeting":
            return "friendly"
        elif message_type == "task_related":
            return "helpful"
        elif message_type == "non_task":
            return "professional"
        else:
            return "neutral"

    def validate_response(self, response: str) -> bool:
        """
        Validate that the generated response meets quality standards.

        Args:
            response (str): The response to validate

        Returns:
            bool: True if the response is valid, False otherwise
        """
        # Check if response is not empty
        if not response or not response.strip():
            return False

        # Check if response is not too long (to prevent rambling responses)
        if len(response) > 200:  # Adjust as needed
            return False

        # Check if response contains placeholder-like content
        if "{{" in response or "}}" in response:
            return False

        return True

    def generate_response_with_validation(self, user_message: str, message_type: str, context: Optional[Dict] = None) -> str:
        """
        Generate a response and validate it before returning.

        Args:
            user_message (str): The original message from the user
            message_type (str): The type of message
            context (Optional[Dict]): Additional context for the conversation

        Returns:
            str: A validated response
        """
        response = self.generate_response(user_message, message_type, context)

        # Validate the response
        if not self.validate_response(response):
            # If validation fails, return a default response
            logger.warning(f"Generated response failed validation: {response}")
            if message_type == "greeting":
                return "Hello! How can I help you with your tasks today?"
            elif message_type == "task_related":
                return "I'm here to help with your task management. What would you like to do?"
            else:
                return "I'm focused on helping with task management. Please keep your questions related to tasks and productivity."

        return response