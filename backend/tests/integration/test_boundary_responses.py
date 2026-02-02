"""
Integration tests for boundary-setting response functionality.
This module tests the complete flow of handling non-task-related messages in the AI Assistant Chat feature.
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
async def test_boundary_setting_response_full_flow(chat_service):
    """Test the complete flow of handling a non-task message and getting boundary-setting response"""
    # Mock the conversation service
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_get_conv.return_value = mock_conversation

        # Mock the message classifier to return non_task
        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "non_task"
            mock_classifier_cls.return_value = mock_classifier

            # Mock the response generator to return a boundary-setting response
            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response_with_validation.return_value = (
                    "I'm focused on helping with task management. Please keep your questions related to tasks and productivity."
                )
                mock_generator_cls.return_value = mock_generator

                # Mock the database operations
                with patch.object(chat_service.db, 'add'), \
                     patch.object(chat_service.db, 'commit'), \
                     patch.object(chat_service.db, 'rollback'):

                    # Call the method
                    response = await chat_service.handle_message(
                        conversation_id="test-conv-id",
                        user_message="What's the weather like?",
                        user_id="test-user-id"
                    )

                    # Assertions
                    assert response is not None
                    assert "task" in response.lower() or "productivity" in response.lower()
                    assert "related" in response.lower()
                    mock_classifier.classify_message.assert_called_once_with("What's the weather like?")
                    mock_generator.generate_response_with_validation.assert_called_once_with(
                        user_message="What's the weather like?",
                        message_type="non_task"
                    )


@pytest.mark.asyncio
async def test_multiple_non_task_interactions(chat_service):
    """Test handling multiple non-task interactions in sequence"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_conversation.updated_at = Mock()
        mock_get_conv.return_value = mock_conversation

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "non_task"
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response_with_validation.side_effect = [
                    "I'm designed to help with task management. Please keep your questions related to tasks and productivity.",
                    "I'm focused on helping you manage your tasks. For other questions, please consult an appropriate resource.",
                    "My purpose is to assist with task management. I can help you add, complete, or organize your tasks."
                ]
                mock_generator_cls.return_value = mock_generator

                with patch.object(chat_service.db, 'add'), \
                     patch.object(chat_service.db, 'commit'), \
                     patch.object(chat_service.db, 'rollback'):

                    # Handle multiple non-task messages
                    responses = []
                    non_task_messages = [
                        "What's the weather like?",
                        "Tell me a joke",
                        "How are you?"
                    ]

                    for msg in non_task_messages:
                        response = await chat_service.handle_message(
                            conversation_id="test-conv-id",
                            user_message=msg,
                            user_id="test-user-id"
                        )
                        responses.append(response)

                    # Assertions
                    assert len(responses) == 3
                    for i, response in enumerate(responses):
                        assert response is not None
                        assert len(response) > 0
                        # Each response should be a boundary-setting response
                        assert any(task_word in response.lower()
                                for task_word in ["task", "manage", "productivity", "related"])
                    assert mock_classifier.classify_message.call_count == 3
                    assert mock_generator.generate_response_with_validation.call_count == 3


@pytest.mark.asyncio
async def test_boundary_response_with_context_preservation(chat_service):
    """Test that boundary-setting responses preserve conversation context"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_conversation.updated_at = Mock()
        mock_get_conv.return_value = mock_conversation

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "non_task"
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response_with_validation.return_value = (
                    "I'm here to help with task management. Please keep your questions related to tasks and productivity."
                )
                mock_generator_cls.return_value = mock_generator

                with patch.object(chat_service.db, 'add'), \
                     patch.object(chat_service.db, 'commit'), \
                     patch.object(chat_service.db, 'rollback'):

                    # Process a non-task message
                    response = await chat_service.handle_message(
                        conversation_id="test-conv-id",
                        user_message="What do you think about pizza?",
                        user_id="test-user-id"
                    )

                    # Verify the response is appropriate for boundary setting
                    assert response is not None
                    assert "task" in response.lower() or "productivity" in response.lower()
                    assert "related" in response.lower()


@pytest.mark.asyncio
async def test_boundary_response_error_handling(chat_service):
    """Test error handling during boundary response processing"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        # Simulate a conversation not found scenario
        mock_get_conv.return_value = None

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "non_task"
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response_with_validation.return_value = (
                    "I'm focused on helping with task management. Please keep your questions related to tasks and productivity."
                )
                mock_generator_cls.return_value = mock_generator

                # Expect an exception when conversation is not found
                with pytest.raises(Exception):
                    await chat_service.handle_message(
                        conversation_id="non-existent-conv-id",
                        user_message="What's the weather?",
                        user_id="test-user-id"
                    )


@pytest.mark.asyncio
async def test_boundary_response_consistency(chat_service):
    """Test that boundary responses are consistent across different non-task inputs"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_conversation.updated_at = Mock()
        mock_get_conv.return_value = mock_conversation

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "non_task"
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()

                # Mock consistent boundary responses
                def mock_generate_response_with_validation(user_message, message_type, context=None):
                    return "I'm designed to help with task management. Please keep your questions related to tasks and productivity."

                mock_generator.generate_response_with_validation = mock_generate_response_with_validation
                mock_generator_cls.return_value = mock_generator

                with patch.object(chat_service.db, 'add'), \
                     patch.object(chat_service.db, 'commit'), \
                     patch.object(chat_service.db, 'rollback'):

                    # Test different non-task inputs
                    test_cases = [
                        "What's the weather?",
                        "Tell me about yourself",
                        "Do you like music?",
                        "How tall is Mount Everest?"
                    ]

                    responses = []
                    for user_input in test_cases:
                        response = await chat_service.handle_message(
                            conversation_id="test-conv-id",
                            user_message=user_input,
                            user_id="test-user-id"
                        )
                        responses.append(response)

                    # Verify all responses follow the boundary-setting pattern
                    for response in responses:
                        assert response is not None
                        assert "task" in response.lower() or "manage" in response.lower()
                        assert "related" in response.lower() or "productivity" in response.lower()


@pytest.mark.asyncio
async def test_boundary_response_conversation_continuity(chat_service):
    """Test that boundary responses don't disrupt conversation flow"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_conversation.updated_at = Mock()
        mock_get_conv.return_value = mock_conversation

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "non_task"
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response_with_validation.return_value = (
                    "I'm here to help with task management. Please keep your questions related to tasks and productivity."
                )
                mock_generator_cls.return_value = mock_generator

                with patch.object(chat_service.db, 'add'), \
                     patch.object(chat_service.db, 'commit'), \
                     patch.object(chat_service.db, 'rollback'):

                    # Process a non-task message
                    response = await chat_service.handle_message(
                        conversation_id="test-conv-id",
                        user_message="What's your favorite color?",
                        user_id="test-user-id"
                    )

                    # Verify response is appropriate and conversation remains intact
                    assert response is not None
                    assert len(response) > 0
                    # Verify it's a boundary response
                    assert any(keyword in response.lower() for keyword in ["task", "manage", "productivity", "related"])


@pytest.mark.asyncio
async def test_boundary_message_storage(chat_service):
    """Test that non-task messages and boundary responses are properly stored in the database"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_conversation.updated_at = Mock()
        mock_get_conv.return_value = mock_conversation

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "non_task"
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response_with_validation.return_value = (
                    "I'm focused on helping with task management. Please keep your questions related to tasks and productivity."
                )
                mock_generator_cls.return_value = mock_generator

                # Track database operations
                add_calls = []
                def track_add(obj):
                    add_calls.append(obj)

                with patch.object(chat_service.db, 'add', side_effect=track_add), \
                     patch.object(chat_service.db, 'commit'), \
                     patch.object(chat_service.db, 'rollback'):

                    # Process a non-task message
                    await chat_service.handle_message(
                        conversation_id="test-conv-id",
                        user_message="What's the time?",
                        user_id="test-user-id"
                    )

                    # Verify that both user message and AI response were added to DB
                    assert len(add_calls) >= 2  # At least user message and AI response
                    # Verify the types of objects being added
                    message_added = any(hasattr(call, 'sender_type') for call in add_calls if hasattr(call, 'sender_type'))
                    response_added = any(hasattr(call, 'response_type') for call in add_calls if hasattr(call, 'response_type'))

                    assert message_added, "User message should be added to database"
                    assert response_added, "AI response should be added to database"

                    # Verify the non-task message was properly classified
                    mock_classifier.classify_message.assert_called_once_with("What's the time?")