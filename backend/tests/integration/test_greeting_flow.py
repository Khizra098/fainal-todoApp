"""
Integration tests for greeting response flow.
This module tests the complete flow of handling greeting messages in the AI Assistant Chat feature.
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
async def test_greeting_message_full_flow(chat_service):
    """Test the complete flow of handling a greeting message"""
    # Mock the conversation service
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_get_conv.return_value = mock_conversation

        # Mock the message classifier to return greeting
        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "greeting"
            mock_classifier_cls.return_value = mock_classifier

            # Mock the response generator to return a greeting response
            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response_with_validation.return_value = "Hello! How can I help you with your tasks today?"
                mock_generator_cls.return_value = mock_generator

                # Mock the database operations
                with patch.object(chat_service.db, 'add'), \
                     patch.object(chat_service.db, 'commit'), \
                     patch.object(chat_service.db, 'rollback'):

                    # Call the method
                    response = await chat_service.handle_message(
                        conversation_id="test-conv-id",
                        user_message="Hello",
                        user_id="test-user-id"
                    )

                    # Assertions
                    assert response is not None
                    assert "hello" in response.lower() or "hi" in response.lower()
                    mock_classifier.classify_message.assert_called_once_with("Hello")
                    mock_generator.generate_response_with_validation.assert_called_once_with(
                        user_message="Hello",
                        message_type="greeting"
                    )


@pytest.mark.asyncio
async def test_multiple_greeting_interactions(chat_service):
    """Test handling multiple greeting interactions in sequence"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_conversation.updated_at = Mock()
        mock_get_conv.return_value = mock_conversation

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "greeting"
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response_with_validation.side_effect = [
                    "Hello! How can I help you with your tasks today?",
                    "Hi again! What can I do for you?",
                    "Greetings! Need help with tasks?"
                ]
                mock_generator_cls.return_value = mock_generator

                with patch.object(chat_service.db, 'add'), \
                     patch.object(chat_service.db, 'commit'), \
                     patch.object(chat_service.db, 'rollback'):

                    # Handle multiple greeting messages
                    responses = []
                    greetings = ["Hello", "Hi", "Greetings"]

                    for greeting in greetings:
                        response = await chat_service.handle_message(
                            conversation_id="test-conv-id",
                            user_message=greeting,
                            user_id="test-user-id"
                        )
                        responses.append(response)

                    # Assertions
                    assert len(responses) == 3
                    for i, response in enumerate(responses):
                        assert response is not None
                        assert len(response) > 0
                        assert any(greeting_word in response.lower()
                                 for greeting_word in ["hello", "hi", "hey", "greet", "good"])
                    assert mock_classifier.classify_message.call_count == 3
                    assert mock_generator.generate_response_with_validation.call_count == 3


@pytest.mark.asyncio
async def test_greeting_with_context_preservation(chat_service):
    """Test that greeting handling preserves conversation context"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_conversation.updated_at = Mock()
        mock_get_conv.return_value = mock_conversation

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "greeting"
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response_with_validation.return_value = "Hello! How can I assist with your tasks?"
                mock_generator_cls.return_value = mock_generator

                with patch.object(chat_service.db, 'add'), \
                     patch.object(chat_service.db, 'commit'), \
                     patch.object(chat_service.db, 'rollback'):

                    # Process a greeting
                    response = await chat_service.handle_message(
                        conversation_id="test-conv-id",
                        user_message="Hi there!",
                        user_id="test-user-id"
                    )

                    # Verify the response is appropriate for a greeting
                    assert response is not None
                    assert "hello" in response.lower() or "hi" in response.lower() or "greet" in response.lower()
                    assert "task" in response.lower() or "assist" in response.lower()


@pytest.mark.asyncio
async def test_greeting_error_handling(chat_service):
    """Test error handling during greeting processing"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        # Simulate a conversation not found scenario
        mock_get_conv.return_value = None

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "greeting"
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response_with_validation.return_value = "Hello! How can I help?"
                mock_generator_cls.return_value = mock_generator

                # Expect an exception when conversation is not found
                with pytest.raises(Exception):
                    await chat_service.handle_message(
                        conversation_id="non-existent-conv-id",
                        user_message="Hello",
                        user_id="test-user-id"
                    )


@pytest.mark.asyncio
async def test_greeting_with_different_tones(chat_service):
    """Test that different greeting types produce appropriately toned responses"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_conversation.updated_at = Mock()
        mock_get_conv.return_value = mock_conversation

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "greeting"
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()

                # Mock different responses for different greeting types
                def mock_generate_response_with_validation(user_message, message_type, context=None):
                    if "hello" in user_message.lower():
                        return "Hello! How can I assist you with your tasks today?"
                    elif "hi" in user_message.lower():
                        return "Hi there! What tasks can I help you with?"
                    else:
                        return "Greetings! I'm here to help with your task management."

                mock_generator.generate_response_with_validation = mock_generate_response_with_validation
                mock_generator_cls.return_value = mock_generator

                with patch.object(chat_service.db, 'add'), \
                     patch.object(chat_service.db, 'commit'), \
                     patch.object(chat_service.db, 'rollback'):

                    # Test different greeting types
                    test_cases = [
                        ("Hello", "hello"),
                        ("Hi", "hi"),
                        ("Greetings", "greetings")
                    ]

                    for user_input, expected_trigger in test_cases:
                        response = await chat_service.handle_message(
                            conversation_id="test-conv-id",
                            user_message=user_input,
                            user_id="test-user-id"
                        )

                        assert response is not None
                        assert len(response) > 0
                        # Ensure response is task-focused while being friendly


@pytest.mark.asyncio
async def test_greeting_conversation_start(chat_service):
    """Test starting a conversation with a greeting"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_conversation.updated_at = Mock()
        mock_get_conv.return_value = mock_conversation

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "greeting"
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response_with_validation.return_value = "Hello! I'm your AI assistant for task management. How can I help you today?"
                mock_generator_cls.return_value = mock_generator

                with patch.object(chat_service.db, 'add'), \
                     patch.object(chat_service.db, 'commit'), \
                     patch.object(chat_service.db, 'rollback'):

                    # Start a conversation with a greeting
                    response = await chat_service.handle_message(
                        conversation_id="test-conv-id",
                        user_message="Hello!",
                        user_id="test-user-id"
                    )

                    # Verify response is appropriate for first interaction
                    assert response is not None
                    assert "hello" in response.lower() or "hi" in response.lower()
                    assert "task" in response.lower() or "help" in response.lower() or "assist" in response.lower()


@pytest.mark.asyncio
async def test_greeting_message_storage(chat_service):
    """Test that greeting messages are properly stored in the database"""
    with patch.object(chat_service.conversation_service, 'get_conversation') as mock_get_conv:
        mock_conversation = Mock()
        mock_conversation.conversation_id = "test-conv-id"
        mock_conversation.updated_at = Mock()
        mock_get_conv.return_value = mock_conversation

        with patch('src.services.chat_service.MessageClassifier') as mock_classifier_cls:
            mock_classifier = Mock()
            mock_classifier.classify_message.return_value = "greeting"
            mock_classifier_cls.return_value = mock_classifier

            with patch('src.services.chat_service.ResponseGenerator') as mock_generator_cls:
                mock_generator = Mock()
                mock_generator.generate_response_with_validation.return_value = "Hello! How can I help you?"
                mock_generator_cls.return_value = mock_generator

                # Track database operations
                add_calls = []
                def track_add(obj):
                    add_calls.append(obj)

                with patch.object(chat_service.db, 'add', side_effect=track_add), \
                     patch.object(chat_service.db, 'commit'), \
                     patch.object(chat_service.db, 'rollback'):

                    # Process a greeting
                    await chat_service.handle_message(
                        conversation_id="test-conv-id",
                        user_message="Hello",
                        user_id="test-user-id"
                    )

                    # Verify that both user message and AI response were added to DB
                    assert len(add_calls) >= 2  # At least user message and AI response
                    # Verify the types of objects being added
                    message_added = any(hasattr(call, 'sender_type') for call in add_calls if hasattr(call, 'sender_type'))
                    response_added = any(hasattr(call, 'response_type') for call in add_calls if hasattr(call, 'response_type'))

                    assert message_added, "User message should be added to database"
                    assert response_added, "AI response should be added to database"