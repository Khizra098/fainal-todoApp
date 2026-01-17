"""Basic AI agent for handling todo commands in the Todo Chatbot."""
import asyncio
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from openai import OpenAI
from ..database import get_db
from ..services.mcp_tool_service import MCPToolService
from .intent_classifier import IntentClassifier, IntentType
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIAgent:
    """
    AI agent that handles todo commands using natural language processing
    and interacts with the system via MCP tools.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the AI agent.

        Args:
            db_session: Database session for operations
        """
        self.db = db_session
        self.intent_classifier = IntentClassifier()
        self.mcp_service = MCPToolService(db_session)

        # Initialize OpenAI client safely
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key and openai_api_key != "your_openai_api_key_here":
            self.openai_client = OpenAI(api_key=openai_api_key)
        else:
            self.openai_client = None  # Will use fallback responses

    def process_message(self, user_id: int, message: str, conversation_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Process a user message and return an appropriate response.

        Args:
            user_id: ID of the user sending the message
            message: The message content from the user
            conversation_id: Optional conversation ID for context

        Returns:
            Dictionary with the response and any actions taken
        """
        # Classify the intent of the message
        intent_result = self.intent_classifier.classify_intent(message)

        # Process based on the classified intent
        if intent_result.intent == IntentType.CREATE_TODO:
            return self._handle_create_todo(user_id, message, intent_result.entities)
        elif intent_result.intent == IntentType.UPDATE_STATUS:
            return self._handle_update_status(user_id, message, intent_result.entities)
        elif intent_result.intent == IntentType.LIST_TODOS:
            return self._handle_list_todos(user_id, intent_result.entities)
        elif intent_result.intent == IntentType.SEARCH_TODOS:
            return self._handle_search_todos(user_id, message, intent_result.entities)
        elif intent_result.intent == IntentType.DELETE_TODO:
            return self._handle_delete_todo(user_id, message, intent_result.entities)
        elif intent_result.intent == IntentType.SET_REMINDER:
            return self._handle_set_reminder(user_id, message, intent_result.entities)
        else:
            # For other intents, provide a helpful response without needing OpenAI
            return self._handle_other_intent(user_id, message)

    def _handle_create_todo(self, user_id: int, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle creating a new todo item."""
        # Extract task description from the message
        description = self._extract_task_description(message)

        # Use entities if available
        due_date_str = entities.get('date')
        priority = entities.get('priority', 'medium')

        # Convert due date string to datetime if possible
        due_date = self._parse_date(due_date_str) if due_date_str else None

        # Call the MCP tool to create the todo
        result = self.mcp_service.create_todo(
            user_id=user_id,
            description=description,
            due_date=due_date,
            priority=priority
        )

        if result['success']:
            return {
                "response": f"I've added '{description}' to your todo list.",
                "action": "create_todo",
                "task": result['task']
            }
        else:
            return {
                "response": f"Sorry, I couldn't add that todo: {result['error']}",
                "action": "create_todo_failed"
            }

    def _handle_update_status(self, user_id: int, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle updating the status of a todo item."""
        # Try to extract task ID from entities or message
        task_id = entities.get('task_id')
        if not task_id:
            # If no explicit task ID, try to find a task by description or ask for clarification
            # For now, we'll ask for clarification
            return {
                "response": "Could you please specify which task you want to mark as completed?",
                "action": "request_clarification"
            }

        # Determine the status to set (usually completed for update_status intent)
        status = entities.get('status', 'completed')

        # Call the MCP tool to update the status
        result = self.mcp_service.update_todo_status(
            user_id=user_id,
            task_id=task_id,
            status=status
        )

        if result['success']:
            return {
                "response": f"I've updated the status of task #{task_id} to {status}.",
                "action": "update_status",
                "task": result['task']
            }
        else:
            return {
                "response": f"Sorry, I couldn't update that task: {result['error']}",
                "action": "update_status_failed"
            }

    def _handle_list_todos(self, user_id: int, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle listing todo items."""
        # Get filters from entities
        status = entities.get('status')

        # Call the MCP tool to list todos
        result = self.mcp_service.list_todos(
            user_id=user_id,
            status=status
        )

        if result['success']:
            tasks = result['tasks']
            if not tasks:
                response = "Your todo list is empty."
            else:
                task_list = "\n".join([f"- {task['id']}: {task['description']} ({task['status']})" for task in tasks])
                status_str = f" that are {status}" if status else ""
                response = f"Here are your tasks{status_str}:\n{task_list}"

            return {
                "response": response,
                "action": "list_todos",
                "tasks": tasks
            }
        else:
            return {
                "response": f"Sorry, I couldn't retrieve your tasks: {result['error']}",
                "action": "list_todos_failed"
            }

    def _handle_search_todos(self, user_id: int, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle searching for todo items."""
        # Get search query from entities or extract from message
        query = entities.get('search_query')
        if not query:
            query = self._extract_search_query(message)

        # Get status filter if available
        status = entities.get('status')

        # Call the MCP tool to search todos
        result = self.mcp_service.search_todos(
            user_id=user_id,
            query=query,
            status=status
        )

        if result['success']:
            tasks = result['tasks']
            if not tasks:
                response = f"I couldn't find any tasks matching '{query}'."
            else:
                task_list = "\n".join([f"- {task['id']}: {task['description']} ({task['status']})" for task in tasks])
                response = f"I found these tasks matching '{query}':\n{task_list}"

            return {
                "response": response,
                "action": "search_todos",
                "tasks": tasks
            }
        else:
            return {
                "response": f"Sorry, I couldn't search your tasks: {result['error']}",
                "action": "search_todos_failed"
            }

    def _handle_delete_todo(self, user_id: int, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle deleting a todo item."""
        # Try to extract task ID from entities or message
        task_id = entities.get('task_id')
        if not task_id:
            return {
                "response": "Could you please specify which task you want to delete?",
                "action": "request_clarification"
            }

        # Call the MCP tool to delete the todo
        result = self.mcp_service.delete_todo(
            user_id=user_id,
            task_id=task_id
        )

        if result['success']:
            return {
                "response": f"I've deleted task #{task_id} from your list.",
                "action": "delete_todo",
                "deleted_task_id": task_id
            }
        else:
            return {
                "response": f"Sorry, I couldn't delete that task: {result['error']}",
                "action": "delete_todo_failed"
            }

    def _handle_set_reminder(self, user_id: int, message: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Handle setting a reminder."""
        # Extract reminder details
        task_id = entities.get('task_id')
        description = entities.get('description')
        date_str = entities.get('date')

        # Parse the date
        remind_at = self._parse_date(date_str) if date_str else None

        # If no description provided, try to extract from message
        if not description:
            description = f"Reminder: {message}"

        # Call the MCP tool to set the reminder
        result = self.mcp_service.set_reminder(
            user_id=user_id,
            task_id=task_id,
            description=description,
            remind_at=remind_at
        )

        if result['success']:
            return {
                "response": f"I've set a reminder for: {description}",
                "action": "set_reminder",
                "reminder": result['reminder']
            }
        else:
            return {
                "response": f"Sorry, I couldn't set that reminder: {result['error']}",
                "action": "set_reminder_failed"
            }

    def _handle_other_intent(self, user_id: int, message: str) -> Dict[str, Any]:
        """Handle other intents with intelligent default responses."""
        # Convert message to lowercase for easier matching
        msg_lower = message.lower()

        # Handle common greetings
        if any(greeting in msg_lower for greeting in ['hello', 'hi', 'hey', 'greetings', 'howdy']):
            return {
                "response": "Hello! I'm your AI assistant for todo management. You can ask me to add, list, complete, or delete tasks.",
                "action": "greeting_response"
            }

        # Handle common questions about wellbeing
        if any(phrase in msg_lower for phrase in ['how are you', 'how do you do', 'how are you doing', 'are you well']):
            return {
                "response": "I'm doing well, thank you for asking! How can I help you manage your tasks today?",
                "action": "wellbeing_response"
            }

        # Handle thanks
        if any(thanks in msg_lower for thanks in ['thank you', 'thanks', 'thx', 'appreciate']):
            return {
                "response": "You're welcome! Is there anything else I can help you with regarding your tasks?",
                "action": "thanks_response"
            }

        # Handle common requests for help
        if any(help_request in msg_lower for help_request in ['help', 'what can you do', 'what do you do', 'commands', 'features']):
            return {
                "response": "I can help you manage your todos! You can ask me to: add a task, list your tasks, mark a task as completed, delete a task, or search for tasks.",
                "action": "help_response"
            }

        # Handle general conversation
        if '?' in message:
            # It's a question - provide a helpful response
            return {
                "response": f"I see you're asking about '{message}'. I'm here to help with your todo list management. You can ask me to add, list, complete, or delete tasks.",
                "action": "question_response"
            }

        # Default response for unrecognized input
        return {
            "response": f"I received your message: '{message}'. I'm your AI assistant for todo management. You can ask me to add, list, complete, or delete tasks.",
            "action": "default_response"
        }

    def _extract_task_description(self, message: str) -> str:
        """Extract the task description from a user message."""
        # Remove common task-creating words to isolate the description
        task_indicators = [
            'add', 'create', 'make', 'new', 'need to', 'want to', 'should', 'must',
            'put', 'write', 'note', 'down', 'on', 'my', 'list', 'todo', 'task', 'item', 'do', 'to-do'
        ]

        clean_message = message.lower()
        for indicator in task_indicators:
            clean_message = re.sub(r'\b' + re.escape(indicator) + r'\b', '', clean_message, flags=re.IGNORECASE)

        # Clean up extra whitespace
        clean_message = re.sub(r'\s+', ' ', clean_message).strip()

        # If we have a clean description, return it; otherwise, return the original message
        return clean_message if clean_message else message

    def _extract_search_query(self, message: str) -> str:
        """Extract the search query from a user message."""
        # Look for what comes after common search words
        search_patterns = [
            r'(?:find|search|look for|show me)\s+(.+?)(?:\s+in|\s+on|\s+from|$)',
            r'(?:where is|locate)\s+(.+?)(?:\s+in|\s+on|\s+from|$)'
        ]

        for pattern in search_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # If no pattern matches, return the original message as a fallback
        return message

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse a date string into a datetime object."""
        # This is a simplified date parser - in a real implementation, you'd want a more robust solution
        if not date_str:
            return None

        # Handle common relative dates
        if date_str.lower() == 'tomorrow':
            from datetime import timedelta
            return datetime.now() + timedelta(days=1)
        elif date_str.lower() == 'today':
            return datetime.now()
        # Add more date parsing logic as needed

        # For now, return None for complex dates - in a real implementation,
        # you'd want to use a library like dateutil.parser
        return None


