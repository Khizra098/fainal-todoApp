"""
Unit tests for the chat service.
This module tests the core functionality of the chat service in the AI Assistant Chat feature.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from datetime import datetime
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.services.chat_service import ChatService
from src.models.conversation import Conversation
from src.models.message import Message
from src.database.database import SessionLocal


@pytest.fixture
def mock_db_session():
    """Create a mock database session for testing"""
    session = Mock(spec=SessionLocal)
    return session


@pytest.fixture
def mock_conversation_service():
    """Create a mock conversation service for testing"""
    service = Mock()
    return service


@pytest.fixture
def chat_service(mock_db_session):
    """Create a chat service instance for testing"""
    return ChatService(mock_db_session)


def test_chat_service_initialization(chat_service, mock_db_session):
    """Test that the chat service initializes correctly"""
    assert chat_service.db == mock_db_session
    assert chat_service.conversation_service is not None
    assert chat_service.message_classifier is not None
    assert chat_service.response_generator is not None


@pytest.mark.asyncio
async def test_handle_message_valid_input(chat_service):
    """Test handling a valid message input"""
    # Mock conversation
    mock_conversation = Mock()
    mock_conversation.conversation_id = "test-conv-id"

    with patch.object(chat_service.conversation_service, 'get_conversation', return_value=mock_conversation):
        with patch.object(chat_service.message_classifier, 'classify_message', return_value="task_related"):
            with patch.object(chat_service.response_generator, 'generate_response_with_validation',
                             return_value="Here's how you can add a task..."):

                with patch.object(chat_service.db, 'add'), \
                     patch.object(chat_service.db, 'commit'), \
                     patch.object(chat_service.db, 'rollback'):

                    response = await chat_service.handle_message(
                        conversation_id="test-conv-id",
                        user_message="How do I add a task?",
                        user_id="test-user-id"
                    )

                    assert response == "Here's how you can add a task..."


@pytest.mark.asyncio
async def test_handle_message_empty_message_raises_error(chat_service):
    """Test that empty messages raise an error"""
    with pytest.raises(Exception):
        await chat_service.handle_message(
            conversation_id="test-conv-id",
            user_message="",
            user_id="test-user-id"
        )


@pytest.mark.asyncio
async def test_handle_message_long_message_raises_error(chat_service):
    """Test that messages exceeding length limit raise an error"""
    long_message = "A" * 10001  # Exceeds 10000 limit

    with pytest.raises(Exception):
        await chat_service.handle_message(
            conversation_id="test-conv-id",
            user_message=long_message,
            user_id="test-user-id"
        )


@pytest.mark.asyncio
async def test_handle_message_conversation_not_found_raises_error(chat_service):
    """Test that non-existent conversations raise an error"""
    with patch.object(chat_service.conversation_service, 'get_conversation', return_value=None):
        with pytest.raises(Exception):
            await chat_service.handle_message(
                conversation_id="non-existent-conv",
                user_message="Hello",
                user_id="test-user-id"
            )


@pytest.mark.asyncio
async def test_get_conversation_history_success(chat_service):
    """Test retrieving conversation history successfully"""
    mock_message1 = Mock()
    mock_message1.to_dict.return_value = {
        "message_id": "msg1",
        "content": "Hello",
        "sender_type": "user",
        "timestamp": "2023-01-01T00:00:00"
    }

    with patch.object(chat_service.conversation_service, 'get_conversation_messages',
                     return_value=[mock_message1]):

        history = await chat_service.get_conversation_history(
            conversation_id="test-conv-id",
            limit=10,
            offset=0
        )

        assert len(history) == 1
        assert history[0]["message_id"] == "msg1"


@pytest.mark.asyncio
async def test_start_new_conversation_success(chat_service):
    """Test starting a new conversation successfully"""
    mock_conversation = Mock()
    mock_conversation.conversation_id = "new-conv-id"

    with patch.object(chat_service.conversation_service, 'create_conversation',
                     return_value=mock_conversation):

        conversation_id = await chat_service.start_new_conversation(
            user_id="test-user-id",
            initial_message="Hello"
        )

        assert conversation_id == "new-conv-id"


@pytest.mark.asyncio
async def test_classify_message_async(chat_service):
    """Test asynchronous message classification"""
    with patch.object(chat_service.message_classifier, 'classify_message',
                     return_value="greeting"):

        result = await chat_service.classify_message_async("Hello")

        assert result == "greeting"


@pytest.mark.asyncio
async def test_generate_response_async(chat_service):
    """Test asynchronous response generation"""
    with patch.object(chat_service.response_generator, 'generate_response_with_validation',
                     return_value="Hello! How can I help?"):

        result = await chat_service.generate_response_async("Hello", "greeting")

        assert result == "Hello! How can I help?"


def test_get_message_analysis(chat_service):
    """Test getting message analysis"""
    with patch.object(chat_service.message_classifier, 'classify_message',
                     return_value="task_related"):
        with patch.object(chat_service.message_classifier, 'get_confidence_scores',
                         return_value={"greeting": 0.1, "task_related": 0.8, "non_task": 0.1}):

            analysis = chat_service.get_message_analysis("How do I add a task?")

            assert analysis["classification"] == "task_related"
            assert "greeting" in analysis["confidence_scores"]
            assert "task_related" in analysis["confidence_scores"]
            assert "non_task" in analysis["confidence_scores"]
            assert "timestamp" in analysis


@pytest.mark.asyncio
async def test_handle_message_classification_mapping(chat_service):
    """Test that message types are correctly mapped to response types"""
    mock_conversation = Mock()
    mock_conversation.conversation_id = "test-conv-id"

    # Test different message classifications
    test_cases = [
        ("task_related", "task_guidance"),
        ("greeting", "greeting"),
        ("non_task", "boundary_setting"),
        ("unknown", "general")
    ]

    for msg_type, expected_resp_type in test_cases:
        with patch.object(chat_service.conversation_service, 'get_conversation', return_value=mock_conversation):
            with patch.object(chat_service.message_classifier, 'classify_message', return_value=msg_type):
                with patch.object(chat_service.response_generator, 'generate_response_with_validation',
                                 return_value="Test response"):

                    # Check the internal mapping function
                    result = chat_service._map_message_type_to_response_type(msg_type)
                    assert result == expected_resp_type


@pytest.mark.asyncio
async def test_handle_message_database_operations(chat_service):
    """Test that database operations are called correctly when handling a message"""
    mock_conversation = Mock()
    mock_conversation.conversation_id = "test-conv-id"
    mock_conversation.updated_at = Mock()

    with patch.object(chat_service.conversation_service, 'get_conversation', return_value=mock_conversation):
        with patch.object(chat_service.message_classifier, 'classify_message', return_value="task_related"):
            with patch.object(chat_service.response_generator, 'generate_response_with_validation',
                             return_value="Here's how to add a task..."):

                # Track database operations
                add_calls = []
                commit_called = False

                def track_add(obj):
                    add_calls.append(obj)

                def track_commit():
                    nonlocal commit_called
                    commit_called = True

                chat_service.db.add = track_add
                chat_service.db.commit = track_commit
                chat_service.db.rollback = Mock()

                await chat_service.handle_message(
                    conversation_id="test-conv-id",
                    user_message="How do I add a task?",
                    user_id="test-user-id"
                )

                # Should add both user message and AI response
                assert len(add_calls) == 2
                assert commit_called


@pytest.mark.asyncio
async def test_handle_message_error_rollback(chat_service):
    """Test that database is rolled back on error"""
    mock_conversation = Mock()
    mock_conversation.conversation_id = "test-conv-id"

    with patch.object(chat_service.conversation_service, 'get_conversation', return_value=mock_conversation):
        with patch.object(chat_service.message_classifier, 'classify_message', side_effect=Exception("Test error")):
            rollback_called = False

            def track_rollback():
                nonlocal rollback_called
                rollback_called = True

            chat_service.db.rollback = track_rollback

            with pytest.raises(Exception):
                await chat_service.handle_message(
                    conversation_id="test-conv-id",
                    user_message="How do I add a task?",
                    user_id="test-user-id"
                )

            assert rollback_called


@pytest.mark.asyncio
async def test_get_conversation_history_error_handling(chat_service):
    """Test error handling in get_conversation_history"""
    with patch.object(chat_service.conversation_service, 'get_conversation_messages',
                     side_effect=Exception("DB Error")):

        with pytest.raises(Exception):
            await chat_service.get_conversation_history("test-conv-id")


@pytest.mark.asyncio
async def test_start_new_conversation_error_handling(chat_service):
    """Test error handling in start_new_conversation"""
    with patch.object(chat_service.conversation_service, 'create_conversation',
                     side_effect=Exception("DB Error")):

        with pytest.raises(Exception):
            await chat_service.start_new_conversation("test-user-id")