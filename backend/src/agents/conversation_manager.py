"""Conversation manager for handling multi-step conversations in the Todo Chatbot."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from ..services.conversation_service import ConversationService
from ..services.task_service import TaskService
from .ai_agent import AIAgent


class ConversationManager:
    """
    Manages conversation state and handles multi-step interactions.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the conversation manager.

        Args:
            db_session: Database session for operations
        """
        self.db = db_session
        self.conversation_service = ConversationService(db_session)
        self.task_service = TaskService(db_session)
        self.ai_agent = AIAgent(db_session)

        # Store ongoing conversation states
        self.conversation_states = {}

    def start_new_conversation(self, user_id: int, initial_message: Optional[str] = None) -> int:
        """
        Start a new conversation for a user.

        Args:
            user_id: ID of the user starting the conversation
            initial_message: Optional initial message to set the conversation title

        Returns:
            ID of the newly created conversation
        """
        title = initial_message[:200] if initial_message and len(initial_message) > 200 else (
            initial_message if initial_message else "New Conversation"
        )
        conversation = self.conversation_service.create_conversation(user_id, title)
        return conversation.id

    def process_message(self, user_id: int, conversation_id: int, message: str) -> Dict[str, Any]:
        """
        Process a message in the context of a conversation.

        Args:
            user_id: ID of the user sending the message
            conversation_id: ID of the conversation
            message: The message content from the user

        Returns:
            Dictionary with the response and any actions taken
        """
        # Add the user's message to the conversation
        self.conversation_service.add_message_to_conversation(
            conversation_id, user_id, "user", message
        )

        # Get the current conversation state
        conversation_state = self._get_or_create_conversation_state(conversation_id)

        # Check if we're in a multi-step process
        if conversation_state.get('awaiting_response'):
            # Handle the response to a previous request for more information
            response = self._handle_multi_step_response(conversation_state, message)
        else:
            # Process the message normally
            response = self.ai_agent.process_message(user_id, message, conversation_id)

        # Add the agent's response to the conversation
        self.conversation_service.add_message_to_conversation(
            conversation_id, user_id, "assistant", response.get("response", "")
        )

        # Update conversation state if needed
        if response.get("action") == "request_clarification":
            conversation_state['awaiting_response'] = True
            conversation_state['pending_action'] = response.get("pending_action")

        return response

    def _get_or_create_conversation_state(self, conversation_id: int) -> Dict[str, Any]:
        """Get or create a conversation state for tracking multi-step interactions."""
        if conversation_id not in self.conversation_states:
            self.conversation_states[conversation_id] = {
                'awaiting_response': False,
                'pending_action': None,
                'step_data': {}
            }
        return self.conversation_states[conversation_id]

    def _handle_multi_step_response(self, conversation_state: Dict[str, Any], message: str) -> Dict[str, Any]:
        """Handle a response to a previous request for more information."""
        # Reset the awaiting state
        conversation_state['awaiting_response'] = False
        pending_action = conversation_state.get('pending_action')

        # In a real implementation, this would continue the multi-step process
        # For now, we'll just return a response indicating the continuation
        response = {
            "response": f"I received your response: '{message}'. Continuing with the previous request...",
            "action": "multi_step_continuation"
        }

        # Clear the pending action
        conversation_state['pending_action'] = None

        return response

    def get_conversation_history(self, user_id: int, conversation_id: int) -> List[Dict[str, Any]]:
        """
        Get the message history for a conversation.

        Args:
            user_id: ID of the user requesting history
            conversation_id: ID of the conversation

        Returns:
            List of messages in the conversation
        """
        messages = self.conversation_service.get_messages_for_conversation(conversation_id, user_id)
        return [
            {
                "id": msg.id,
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat() if msg.timestamp else None
            }
            for msg in messages
        ]

    def end_conversation(self, user_id: int, conversation_id: int) -> bool:
        """
        End a conversation by archiving it.

        Args:
            user_id: ID of the user who owns the conversation
            conversation_id: ID of the conversation to end

        Returns:
            True if the conversation was ended, False otherwise
        """
        return self.conversation_service.archive_conversation(conversation_id, user_id)

    def get_active_conversations(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all active conversations for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of active conversations
        """
        conversations = self.conversation_service.get_user_conversations(
            user_id, status=None  # Get all conversations regardless of status
        )
        return [
            {
                "id": conv.id,
                "title": conv.title,
                "status": conv.status.value,
                "created_at": conv.created_at.isoformat() if conv.created_at else None,
                "updated_at": conv.updated_at.isoformat() if conv.updated_at else None
            }
            for conv in conversations
        ]

    def create_recurring_task(self, user_id: int, conversation_id: int, task_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the creation of a recurring task through multi-step conversation.

        Args:
            user_id: ID of the user creating the task
            conversation_id: ID of the current conversation
            task_details: Details of the task to create

        Returns:
            Dictionary with the result of the operation
        """
        # This would involve a multi-step conversation to collect all necessary details
        # For now, we'll just return a placeholder response
        conversation_state = self._get_or_create_conversation_state(conversation_id)

        # Check if we're in the middle of collecting recurring task details
        if conversation_state.get('collecting_recurring_details'):
            # Process the response to a previous question about recurrence
            step_data = conversation_state.get('step_data', {})

            # Update step data with the new information
            step_data.update(task_details)

            if self._has_required_recurring_details(step_data):
                # All required details are collected, create the task
                result = self._create_final_recurring_task(user_id, step_data)
                conversation_state['collecting_recurring_details'] = False
                conversation_state['step_data'] = {}

                return result
            else:
                # Still need more details, ask for the next piece of information
                next_question = self._get_next_recurring_detail_prompt(step_data)
                conversation_state['step_data'] = step_data

                return {
                    "response": next_question,
                    "action": "request_more_details",
                    "awaiting_response": True
                }
        else:
            # Start the process of creating a recurring task
            conversation_state['collecting_recurring_details'] = True
            conversation_state['step_data'] = {'initial_request': task_details}

            # Ask for the first required detail
            first_question = self._get_next_recurring_detail_prompt({})
            return {
                "response": first_question,
                "action": "request_initial_details",
                "awaiting_response": True
            }

    def _has_required_recurring_details(self, step_data: Dict[str, Any]) -> bool:
        """Check if all required details for a recurring task are collected."""
        # Placeholder implementation - define what details are required
        required_fields = ['description', 'recurrence_pattern']
        return all(field in step_data for field in required_fields)

    def _get_next_recurring_detail_prompt(self, step_data: Dict[str, Any]) -> str:
        """Get the next question to ask for a recurring task."""
        if 'description' not in step_data:
            return "What task would you like to repeat?"
        elif 'recurrence_pattern' not in step_data:
            return "How often should this task repeat? (daily, weekly, monthly, etc.)"
        elif 'end_date' not in step_data:
            return "When should this recurring task stop? (or say 'never' to repeat indefinitely)"
        else:
            # All required details collected
            return ""

    def _create_final_recurring_task(self, user_id: int, task_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create the final recurring task after collecting all details."""
        # For now, create a regular task as a placeholder
        # In a real implementation, this would create a recurring task entry

        # Create a regular task for now
        result = self.ai_agent.process_message(
            user_id,
            f"Add {task_details.get('description', 'a recurring task')} to my list"
        )

        return {
            "response": f"I've created the recurring task: {task_details.get('description', 'unnamed task')}. It will repeat {task_details.get('recurrence_pattern', 'periodically')}.",
            "action": "create_recurring_task_success",
            "task_details": task_details
        }