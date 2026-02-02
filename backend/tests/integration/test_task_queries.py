"""
Integration tests for task-related message handling.
This module tests the full flow of handling task-related queries.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.services.chat_service import ChatService
from src.services.message_classifier import MessageClassifier
from src.services.response_generator import ResponseGenerator
from src.models.conversation import Conversation
from src.models.message import Message
from src.database.database import SessionLocal


@pytest.fixture
def mock_db_session():
    """Create a mock database session for testing"""
    session = Mock(spec=SessionLocal)
    return session


@pytest.fixture
def chat_service(mock_db_session):
    """Create a chat service instance for testing"""
    return ChatService(mock_db_session)


@pytest.mark.asyncio
async def test_handle_task_related_query_integration(chat_service):
    """Test the full integration of handling a task-related query"""
    # Mock the conversation service
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_get_conv.return_value = mock_conversation

        # Mock the message classifier
        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "task_related"
            mock_classifier_cls.return_value = mock_classifier

            # Mock the response generator
            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response.return_value = "Here's how you can add a task..."
                mock_generator_cls.return_value = mock_generator

                # Call the method
                response = await chat_service.handle_message(
                    conversation_id="test-conv-id",
                    user_message="How do I add a new task?",
                    user_id="test-user-id"
                )

                # Assertions
                assert response is not None
                assert "task" in response.lower()
                mock_classifier.classify_message.assert_called_once_with("How do I add a new task?")
                mock_generator.generate_response.assert_called_once_with("How do I add a new task?", "task_related")


@pytest.mark.asyncio
async def test_handle_multiple_task_queries_in_sequence(chat_service):
    """Test handling multiple task queries in sequence within a conversation"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_get_conv.return_value = mock_conversation

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.side_effect = ["task_related", "task_related", "task_related"]
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response.side_effect = [
                    "To add a task, use the add button",
                    "To complete a task, click the checkbox",
                    "To delete a task, use the delete button"
                ]
                mock_generator_cls.return_value = mock_generator

                # Handle multiple queries
                responses = []
                queries = [
                    "How do I add a task?",
                    "How do I complete a task?",
                    "How do I delete a task?"
                ]

                for query in queries:
                    response = await chat_service.handle_message(
                        conversation_id="test-conv-id",
                        user_message=query,
                        user_id="test-user-id"
                    )
                    responses.append(response)

                # Assertions
                assert len(responses) == 3
                for i, response in enumerate(responses):
                    assert response is not None
                    assert len(response) > 0
                assert mock_classifier.classify_message.call_count == 3
                assert mock_generator.generate_response.call_count == 3


@pytest.mark.asyncio
async def test_handle_task_query_with_context(chat_service):
    """Test handling a task query with conversation context"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_get_conv.return_value = mock_conversation

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "task_related"
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                # Mock a response that takes context into account
                def generate_mock_response(user_input, message_type, context=None):
                    if "add" in user_input.lower():
                        return "To add a task, click the 'Add Task' button in the top toolbar."
                    elif "complete" in user_input.lower():
                        return "To complete a task, click the checkbox next to the task."
                    else:
                        return "I can help you with task management. Try asking about adding, completing, or deleting tasks."

                mock_generator.generate_response = generate_mock_response
                mock_generator_cls.return_value = mock_generator

                # Test a specific task query
                response = await chat_service.handle_message(
                    conversation_id="test-conv-id",
                    user_message="How do I add a new task?",
                    user_id="test-user-id"
                )

                # Assertions
                assert response is not None
                assert "add" in response.lower() or "task" in response.lower()
                assert "button" in response.lower()


@pytest.mark.asyncio
async def test_handle_task_query_error_handling(chat_service):
    """Test error handling in task query processing"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        # Simulate a conversation not found scenario
        mock_get_conv.return_value = None

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "task_related"
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response.return_value = "Here's how to manage tasks..."
                mock_generator_cls.return_value = mock_generator

                # Expect an exception when conversation is not found
                with pytest.raises(Exception):
                    await chat_service.handle_message(
                        conversation_id="non-existent-conv-id",
                        user_message="How do I add a task?",
                        user_id="test-user-id"
                    )


@pytest.mark.asyncio
async def test_handle_task_query_empty_message(chat_service):
    """Test handling an empty task query message"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_get_conv.return_value = mock_conversation

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "greeting"  # Empty message might be treated as greeting
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response.return_value = "Hello! How can I help you with tasks today?"
                mock_generator_cls.return_value = mock_generator

                # Test with empty message
                response = await chat_service.handle_message(
                    conversation_id="test-conv-id",
                    user_message="",
                    user_id="test-user-id"
                )

                # Should handle empty message gracefully
                assert response is not None
                assert isinstance(response, str)


@pytest.mark.asyncio
async def test_conversation_state_preservation(chat_service):
    """Test that conversation state is properly preserved during task queries"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_get_conv.return_value = mock_conversation

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "task_related"
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response.return_value = "Here's how to manage your tasks..."
                mock_generator_cls.return_value = mock_generator

                # Process multiple related queries
                response1 = await chat_service.handle_message(
                    conversation_id="test-conv-id",
                    user_message="How do I add a task?",
                    user_id="test-user-id"
                )

                response2 = await chat_service.handle_message(
                    conversation_id="test-conv-id",
                    user_message="How do I edit that task?",
                    user_id="test-user-id"
                )

                # Both responses should be valid
                assert response1 is not None and response2 is not None
                assert len(response1) > 0 and len(response2) > 0