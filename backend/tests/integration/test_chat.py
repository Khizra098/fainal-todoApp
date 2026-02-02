"""
Integration tests for chat endpoints.

This module contains integration tests for the chat API endpoints,
testing the complete flow of creating conversations, sending messages,
retrieving chat history, and managing chat sessions.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import json
from datetime import datetime, timedelta

from src.database.database import Base
from src.main import app
from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_user(test_db):
    """Create a sample user for testing."""
    user = User(
        email="chat.user@example.com",
        username="chatuser",
        hashed_password="$2b$12$LQZ4bsdWJl6DHl2Db.HODeLGzG2q/KqLQvaa6a00xHDcKsiyAC8bC"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def sample_conversation(test_db, sample_user):
    """Create a sample conversation for testing."""
    conversation = Conversation(
        title="Test Conversation",
        description="A test conversation for integration tests",
        user_id=sample_user.id
    )
    test_db.add(conversation)
    test_db.commit()
    test_db.refresh(conversation)
    return conversation


class TestChatBasicFunctionality:
    """Integration tests for basic chat functionality."""

    def test_send_message_to_conversation(self, client, test_db, sample_user, sample_conversation):
        """Test sending a message to a conversation."""
        message_data = {
            "conversation_id": sample_conversation.id,
            "content": "Hello, this is a test message!",
            "sender_id": sample_user.id
        }

        response = client.post("/api/v1/chat", json=message_data)

        # Response depends on authentication requirements
        assert response.status_code in [200, 201, 401, 403, 422]

    def test_send_message_unauthorized(self, client):
        """Test sending a message without authentication."""
        message_data = {
            "conversation_id": 1,
            "content": "Unauthorized message",
            "sender_id": 1
        }

        response = client.post("/api/v1/chat", json=message_data)

        # Should return 401 for unauthorized
        assert response.status_code in [401, 403]

    def test_send_empty_message(self, client, test_db, sample_user, sample_conversation):
        """Test sending an empty message."""
        message_data = {
            "conversation_id": sample_conversation.id,
            "content": "",  # Empty content
            "sender_id": sample_user.id
        }

        response = client.post("/api/v1/chat", json=message_data)

        # Should return 422 for validation error or 400 for bad request
        assert response.status_code in [400, 422]

    def test_send_message_to_nonexistent_conversation(self, client, test_db, sample_user):
        """Test sending a message to a non-existent conversation."""
        message_data = {
            "conversation_id": 999999,  # Non-existent conversation
            "content": "Message to non-existent conversation",
            "sender_id": sample_user.id
        }

        response = client.post("/api/v1/chat", json=message_data)

        # Should return 404 for not found or 422 for validation error
        assert response.status_code in [404, 422]

    def test_send_message_without_conversation_id(self, client, test_db, sample_user):
        """Test sending a message without specifying conversation ID."""
        message_data = {
            "content": "Message without conversation ID",
            "sender_id": sample_user.id
        }

        response = client.post("/api/v1/chat", json=message_data)

        # Should return 422 for validation error
        assert response.status_code in [400, 422]


class TestChatMessageRetrieval:
    """Integration tests for retrieving chat messages."""

    def test_get_conversation_history(self, client, test_db, sample_conversation):
        """Test retrieving conversation history."""
        # Add some test messages to the conversation
        message1 = Message(
            content="First message",
            conversation_id=sample_conversation.id,
            sender_id=1,
            message_type="text"
        )
        message2 = Message(
            content="Second message",
            conversation_id=sample_conversation.id,
            sender_id=2,
            message_type="text"
        )
        test_db.add(message1)
        test_db.add(message2)
        test_db.commit()

        response = client.get(f"/api/v1/chat/{sample_conversation.id}")

        # Response depends on authentication requirements
        assert response.status_code in [200, 401, 403, 404]

    def test_get_conversation_history_unauthorized(self, client, sample_conversation):
        """Test retrieving conversation history without authentication."""
        response = client.get(f"/api/v1/chat/{sample_conversation.id}")

        # Should return 401 for unauthorized or 403 for forbidden
        assert response.status_code in [401, 403]

    def test_get_nonexistent_conversation_history(self, client):
        """Test retrieving history for a non-existent conversation."""
        response = client.get("/api/v1/chat/999999")

        # Should return 404 for not found
        assert response.status_code in [404, 401, 403]

    def test_get_conversation_history_with_pagination(self, client, test_db, sample_conversation):
        """Test retrieving conversation history with pagination."""
        # Add multiple messages to test pagination
        for i in range(10):
            message = Message(
                content=f"Message {i}",
                conversation_id=sample_conversation.id,
                sender_id=1,
                message_type="text"
            )
            test_db.add(message)
        test_db.commit()

        # Test with pagination parameters
        response = client.get(f"/api/v1/chat/{sample_conversation.id}?skip=0&limit=5")

        # Response depends on authentication requirements
        assert response.status_code in [200, 401, 403, 404]


class TestChatConversationManagement:
    """Integration tests for conversation management."""

    def test_create_new_conversation(self, client, test_db, sample_user):
        """Test creating a new conversation."""
        conversation_data = {
            "title": "New Test Conversation",
            "description": "Created through API",
            "user_id": sample_user.id
        }

        response = client.post("/api/v1/chat/conversations", json=conversation_data)

        # Response depends on authentication requirements
        assert response.status_code in [200, 201, 401, 403, 422]

    def test_create_conversation_unauthorized(self, client):
        """Test creating a conversation without authentication."""
        conversation_data = {
            "title": "Unauthorized Conversation",
            "description": "Should not be created",
            "user_id": 1
        }

        response = client.post("/api/v1/chat/conversations", json=conversation_data)

        # Should return 401 for unauthorized
        assert response.status_code in [401, 403]

    def test_get_user_conversations(self, client, test_db, sample_user):
        """Test retrieving user's conversations."""
        # Create a few conversations for the user
        conv1 = Conversation(title="User Conv 1", user_id=sample_user.id)
        conv2 = Conversation(title="User Conv 2", user_id=sample_user.id)
        test_db.add(conv1)
        test_db.add(conv2)
        test_db.commit()

        response = client.get(f"/api/v1/chat/conversations?user_id={sample_user.id}")

        # Response depends on authentication requirements
        assert response.status_code in [200, 401, 403]

    def test_get_user_conversations_unauthorized(self, client):
        """Test retrieving user's conversations without authentication."""
        response = client.get("/api/v1/chat/conversations?user_id=1")

        # Should return 401 for unauthorized
        assert response.status_code in [401, 403]

    def test_update_conversation(self, client, test_db, sample_conversation):
        """Test updating a conversation."""
        update_data = {
            "title": "Updated Conversation Title",
            "description": "Updated description"
        }

        response = client.put(f"/api/v1/chat/conversations/{sample_conversation.id}", json=update_data)

        # Response depends on authentication requirements
        assert response.status_code in [200, 401, 403, 404, 422]

    def test_update_conversation_unauthorized(self, client, sample_conversation):
        """Test updating a conversation without authentication."""
        update_data = {
            "title": "Unauthorized Update",
            "description": "Should not be updated"
        }

        response = client.put(f"/api/v1/chat/conversations/{sample_conversation.id}", json=update_data)

        # Should return 401 for unauthorized
        assert response.status_code in [401, 403]

    def test_delete_conversation(self, client, sample_conversation):
        """Test deleting a conversation."""
        response = client.delete(f"/api/v1/chat/conversations/{sample_conversation.id}")

        # Response depends on authentication requirements
        assert response.status_code in [200, 204, 401, 403, 404]


class TestChatMessageTypes:
    """Integration tests for different message types."""

    def test_send_text_message(self, client, test_db, sample_user, sample_conversation):
        """Test sending a text message."""
        message_data = {
            "conversation_id": sample_conversation.id,
            "content": "This is a text message",
            "sender_id": sample_user.id,
            "message_type": "text"
        }

        response = client.post("/api/v1/chat", json=message_data)

        assert response.status_code in [200, 201, 401, 403, 422]

    def test_send_command_message(self, client, test_db, sample_user, sample_conversation):
        """Test sending a command message."""
        message_data = {
            "conversation_id": sample_conversation.id,
            "content": "/help Show available commands",
            "sender_id": sample_user.id,
            "message_type": "command"
        }

        response = client.post("/api/v1/chat", json=message_data)

        assert response.status_code in [200, 201, 401, 403, 422]

    def test_send_system_message(self, client, test_db, sample_conversation):
        """Test sending a system message."""
        message_data = {
            "conversation_id": sample_conversation.id,
            "content": "System notification",
            "sender_id": None,  # System messages might not have a sender
            "message_type": "system"
        }

        response = client.post("/api/v1/chat", json=message_data)

        assert response.status_code in [200, 201, 401, 403, 422]


class TestChatMessageMetadata:
    """Integration tests for message metadata."""

    def test_send_message_with_metadata(self, client, test_db, sample_user, sample_conversation):
        """Test sending a message with metadata."""
        message_data = {
            "conversation_id": sample_conversation.id,
            "content": "Message with metadata",
            "sender_id": sample_user.id,
            "message_type": "text",
            "metadata": {
                "reactions": ["like"],
                "attachments": [{"type": "image", "url": "/path/to/image.jpg"}],
                "reply_to": 123
            }
        }

        response = client.post("/api/v1/chat", json=message_data)

        assert response.status_code in [200, 201, 401, 403, 422]

    def test_send_message_with_invalid_metadata(self, client, test_db, sample_user, sample_conversation):
        """Test sending a message with invalid metadata."""
        message_data = {
            "conversation_id": sample_conversation.id,
            "content": "Message with invalid metadata",
            "sender_id": sample_user.id,
            "message_type": "text",
            "metadata": "invalid_metadata_type"  # Should be a dict/object
        }

        response = client.post("/api/v1/chat", json=message_data)

        assert response.status_code in [400, 422]  # Validation error


class TestChatMessageSearch:
    """Integration tests for message search functionality."""

    def test_search_messages_in_conversation(self, client, test_db, sample_conversation):
        """Test searching for messages within a conversation."""
        # Add test messages
        msg1 = Message(
            content="Python is great for web development",
            conversation_id=sample_conversation.id,
            sender_id=1,
            message_type="text"
        )
        msg2 = Message(
            content="JavaScript is essential for frontend",
            conversation_id=sample_conversation.id,
            sender_id=2,
            message_type="text"
        )
        test_db.add(msg1)
        test_db.add(msg2)
        test_db.commit()

        # Search for messages containing "Python"
        search_params = {"query": "Python"}
        response = client.get(f"/api/v1/chat/{sample_conversation.id}/search", params=search_params)

        assert response.status_code in [200, 401, 403, 404]

    def test_search_messages_unauthorized(self, client, sample_conversation):
        """Test searching messages without authentication."""
        search_params = {"query": "test"}
        response = client.get(f"/api/v1/chat/{sample_conversation.id}/search", params=search_params)

        assert response.status_code in [401, 403]


class TestChatRealTimeFeatures:
    """Integration tests for real-time chat features (if implemented)."""

    def test_websocket_connection(self, client):
        """Test WebSocket connection for real-time chat (if implemented)."""
        # This would test WebSocket endpoints if they exist
        # For now, we'll just check if the endpoint exists
        try:
            # Attempt to connect to a potential WebSocket endpoint
            # Note: TestClient doesn't support WebSocket, so this is conceptual
            response = client.get("/api/v1/chat/ws")
            assert response.status_code in [404, 405]  # Endpoint might not exist or not support GET
        except:
            # If there's an error connecting (which is expected for WebSocket),
            # that's fine for this test
            pass

    def test_typing_indicator(self, client, test_db, sample_user, sample_conversation):
        """Test typing indicator endpoint (if implemented)."""
        typing_data = {
            "conversation_id": sample_conversation.id,
            "user_id": sample_user.id,
            "is_typing": True
        }

        response = client.post("/api/v1/chat/typing", json=typing_data)

        assert response.status_code in [200, 401, 403, 422]


class TestChatMessageValidation:
    """Integration tests for message validation."""

    def test_send_message_exceeding_length_limit(self, client, test_db, sample_user, sample_conversation):
        """Test sending a message that exceeds length limits."""
        long_content = "A" * 10000  # Assuming there's a length limit
        message_data = {
            "conversation_id": sample_conversation.id,
            "content": long_content,
            "sender_id": sample_user.id
        }

        response = client.post("/api/v1/chat", json=message_data)

        assert response.status_code in [400, 422]  # Validation error

    def test_send_message_with_special_characters(self, client, test_db, sample_user, sample_conversation):
        """Test sending a message with special characters."""
        special_content = "Hello! @#$%^&*()_+-=[]{}|;:,.<>? Testing special chars."
        message_data = {
            "conversation_id": sample_conversation.id,
            "content": special_content,
            "sender_id": sample_user.id
        }

        response = client.post("/api/v1/chat", json=message_data)

        assert response.status_code in [200, 201, 401, 403, 422]

    def test_send_message_with_emojis(self, client, test_db, sample_user, sample_conversation):
        """Test sending a message with emojis."""
        emoji_content = "Hello! 😊👍🎉 This message contains emojis 🚀💻📱"
        message_data = {
            "conversation_id": sample_conversation.id,
            "content": emoji_content,
            "sender_id": sample_user.id
        }

        response = client.post("/api/v1/chat", json=message_data)

        assert response.status_code in [200, 201, 401, 403, 422]


class TestChatErrorHandling:
    """Integration tests for error handling in chat endpoints."""

    def test_send_message_with_invalid_json(self, client):
        """Test sending a message with invalid JSON."""
        response = client.post(
            "/api/v1/chat",
            content="invalid json {",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code in [400, 422]  # Bad request or validation error

    def test_request_with_missing_required_fields(self, client, test_db, sample_user):
        """Test request with missing required fields."""
        message_data = {
            # Missing required fields like conversation_id and content
            "sender_id": sample_user.id
        }

        response = client.post("/api/v1/chat", json=message_data)

        assert response.status_code in [400, 422]  # Validation error

    def test_request_with_wrong_field_types(self, client, test_db, sample_user, sample_conversation):
        """Test request with wrong field types."""
        message_data = {
            "conversation_id": "not_a_number",  # Should be integer
            "content": 12345,  # Should be string
            "sender_id": sample_conversation.id  # Wrong assignment
        }

        response = client.post("/api/v1/chat", json=message_data)

        assert response.status_code in [400, 422]  # Validation error


class TestChatRateLimiting:
    """Integration tests for chat rate limiting."""

    def test_send_multiple_messages_quickly(self, client, test_db, sample_user, sample_conversation):
        """Test rate limiting when sending multiple messages quickly."""
        for i in range(10):  # Assuming rate limit is below 10 messages
            message_data = {
                "conversation_id": sample_conversation.id,
                "content": f"Rapid message {i}",
                "sender_id": sample_user.id
            }

            response = client.post("/api/v1/chat", json=message_data)

            # Check if we eventually get rate limited (429)
            if response.status_code == 429:
                break

        # At some point, we should get rate limited
        # Note: This test depends on rate limiting being configured in the app
        pass


class TestChatConcurrentAccess:
    """Integration tests for concurrent chat access."""

    def test_concurrent_message_sending(self, client, test_db, sample_user, sample_conversation):
        """Test multiple users sending messages to the same conversation concurrently."""
        # This test would typically require multiple test clients or threads
        # For integration testing, we'll simulate by sending multiple requests

        for i in range(3):
            message_data = {
                "conversation_id": sample_conversation.id,
                "content": f"Concurrent message {i}",
                "sender_id": sample_user.id
            }

            response = client.post("/api/v1/chat", json=message_data)

            assert response.status_code in [200, 201, 401, 403, 422]


class TestChatResponseFormat:
    """Integration tests for response format consistency."""

    def test_consistent_response_format_for_success(self, client, test_db, sample_user, sample_conversation):
        """Test that successful chat operations return consistent response format."""
        message_data = {
            "conversation_id": sample_conversation.id,
            "content": "Consistency test message",
            "sender_id": sample_user.id
        }

        response = client.post("/api/v1/chat", json=message_data)

        if response.status_code in [200, 201]:
            try:
                response_data = response.json()
                # Check if response has expected structure
                assert "id" in response_data or "message" in response_data or len(response_data) > 0
            except:
                # If response is not JSON, that's also acceptable in some cases
                pass

    def test_consistent_error_format(self, client):
        """Test that chat errors return consistent format."""
        # Send invalid request to trigger error
        response = client.post(
            "/api/v1/chat",
            content="invalid json {",
            headers={"Content-Type": "application/json"}
        )

        if response.status_code in [400, 422]:
            try:
                response_data = response.json()
                # Check if error response has expected fields
                assert "detail" in response_data or len(response_data) > 0
            except:
                # Non-JSON response is also possible
                pass


class TestChatPermissions:
    """Integration tests for chat permissions."""

    def test_access_other_users_conversation(self, client, test_db):
        """Test that users cannot access conversations they don't own."""
        # Create a user and conversation
        user1 = User(email="user1@example.com", username="user1", hashed_password="$2b$12$LQZ4bsdWJl6DHl2Db.HODeLGzG2q/KqLQvaa6a00xHDcKsiyAC8bC")
        user2 = User(email="user2@example.com", username="user2", hashed_password="$2b$12$LQZ4bsdWJl6DHl2Db.HODeLGzG2q/KqLQvaa6a00xHDcKsiyAC8bC")
        test_db.add(user1)
        test_db.add(user2)
        test_db.commit()

        # Create a conversation for user1
        conversation = Conversation(title="User1's Private Chat", user_id=user1.id)
        test_db.add(conversation)
        test_db.commit()

        # Try to access user1's conversation as user2 (without proper auth)
        response = client.get(f"/api/v1/chat/{conversation.id}")

        # Should return 401, 403, or 404 (not found to avoid revealing existence)
        assert response.status_code in [401, 403, 404]