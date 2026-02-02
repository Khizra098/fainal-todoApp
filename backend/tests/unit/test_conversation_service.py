"""
Unit tests for the ConversationService.

This module contains unit tests for the ConversationService class including validation,
business logic, and data access operations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.services.conversation_service import ConversationService
from src.models.conversation import Conversation
from src.models.message import Message
from src.models.user import User


class TestConversationServiceBasic:
    """Basic tests for the ConversationService."""

    def test_conversation_service_initialization(self):
        """Test initializing ConversationService with a database session."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        assert service.db == mock_db


class TestConversationServiceConversationCreation:
    """Tests for conversation creation functionality."""

    def test_create_conversation_with_valid_data(self):
        """Test creating a conversation with valid data."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the conversation creation
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = 1
        mock_conversation.title = "Test Conversation"
        mock_conversation.user_id = 1
        mock_conversation.is_active = True

        # Since we can't instantiate a real Conversation without the full model,
        # we'll test the service method logic
        with patch('src.services.conversation_service.Conversation') as mock_conversation_class:
            instance = Mock()
            instance.id = 1
            instance.title = "Test Conversation"
            instance.user_id = 1
            instance.is_active = True
            mock_conversation_class.return_value = instance

            result = service.create_conversation(
                title="Test Conversation",
                description="A test conversation",
                user_id=1
            )

            # Verify the conversation was added to the session
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

            # Verify the result
            assert result.title == "Test Conversation"
            assert result.user_id == 1

    def test_create_conversation_with_defaults(self):
        """Test creating a conversation with default values."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        with patch('src.services.conversation_service.Conversation') as mock_conversation_class:
            instance = Mock()
            instance.id = 1
            instance.title = "Untitled Conversation"  # Default title
            instance.user_id = 1
            instance.is_active = True  # Default active status
            instance.metadata = {}  # Default metadata
            mock_conversation_class.return_value = instance

            result = service.create_conversation(
                user_id=1
            )

            # Verify the conversation was created with default values
            assert result.title == "Untitled Conversation"
            assert result.is_active is True
            assert result.metadata == {}


class TestConversationServiceConversationRetrieval:
    """Tests for conversation retrieval functionality."""

    def test_get_conversation_by_id(self):
        """Test retrieving a conversation by ID."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the query result
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = 1
        mock_conversation.title = "Found Conversation"
        mock_conversation.user_id = 1

        mock_query = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_conversation

        result = service.get_conversation_by_id(1)

        # Verify the query was constructed correctly
        mock_db.query.assert_called_once_with(Conversation)
        assert result == mock_conversation

    def test_get_conversation_by_id_not_found(self):
        """Test retrieving a non-existent conversation by ID returns None."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the query result to return None
        mock_query = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        result = service.get_conversation_by_id(999)

        assert result is None

    def test_get_conversations_by_user(self):
        """Test retrieving conversations by user ID."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the query result
        mock_conversations = [
            Mock(spec=Conversation, id=1, title="User Conv 1", user_id=1),
            Mock(spec=Conversation, id=2, title="User Conv 2", user_id=1)
        ]

        mock_query = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = mock_conversations

        result = service.get_conversations_by_user(user_id=1)

        # Verify the query was constructed correctly
        mock_db.query.assert_called_once_with(Conversation)
        assert result == mock_conversations

    def test_get_conversations_by_user_with_pagination(self):
        """Test retrieving conversations by user with pagination."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the query result
        mock_conversations = [
            Mock(spec=Conversation, id=1, title="User Conv 1", user_id=1),
            Mock(spec=Conversation, id=2, title="User Conv 2", user_id=1)
        ]

        mock_query = Mock()
        mock_filter = Mock()
        mock_offset = Mock()
        mock_limit = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.offset.return_value = mock_offset
        mock_offset.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_conversations

        result = service.get_conversations_by_user_paginated(user_id=1, skip=0, limit=10)

        # Verify the query was constructed with offset and limit
        mock_db.query.assert_called_once_with(Conversation)
        mock_filter.offset.assert_called_once_with(0)
        mock_offset.limit.assert_called_once_with(10)
        assert result == mock_conversations

    def test_get_active_conversations_by_user(self):
        """Test retrieving only active conversations by user ID."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the query result
        mock_conversations = [
            Mock(spec=Conversation, id=1, title="Active Conv", user_id=1, is_active=True),
        ]

        mock_query = Mock()
        mock_filter = Mock()
        mock_filter2 = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.filter.return_value = mock_filter2
        mock_filter2.all.return_value = mock_conversations

        result = service.get_active_conversations_by_user(user_id=1)

        # Verify the query was constructed with both filters
        mock_db.query.assert_called_once_with(Conversation)
        assert result == mock_conversations


class TestConversationServiceConversationUpdates:
    """Tests for conversation update functionality."""

    def test_update_conversation_title(self):
        """Test updating conversation title."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock an existing conversation
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = 1
        mock_conversation.title = "Original Title"
        mock_conversation.user_id = 1

        # Mock the get_conversation_by_id method to return the conversation
        with patch.object(service, 'get_conversation_by_id', return_value=mock_conversation):
            updated_conversation = service.update_conversation(
                conversation_id=1,
                title="Updated Title"
            )

            # Verify the title was updated
            assert mock_conversation.title == "Updated Title"

            # Verify the session was committed and refreshed
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_conversation)

            assert updated_conversation == mock_conversation

    def test_update_conversation_description(self):
        """Test updating conversation description."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock an existing conversation
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = 1
        mock_conversation.title = "Test Title"
        mock_conversation.description = "Original Description"
        mock_conversation.user_id = 1

        # Mock the get_conversation_by_id method to return the conversation
        with patch.object(service, 'get_conversation_by_id', return_value=mock_conversation):
            updated_conversation = service.update_conversation(
                conversation_id=1,
                description="Updated Description"
            )

            # Verify the description was updated
            assert mock_conversation.description == "Updated Description"

            # Verify the session was committed and refreshed
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_conversation)

            assert updated_conversation == mock_conversation

    def test_update_conversation_metadata(self):
        """Test updating conversation metadata."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock an existing conversation
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = 1
        mock_conversation.title = "Test Title"
        mock_conversation.user_id = 1
        mock_conversation.metadata = {"category": "support", "priority": "low"}

        # Mock the get_conversation_by_id method to return the conversation
        with patch.object(service, 'get_conversation_by_id', return_value=mock_conversation):
            new_metadata = {"category": "sales", "priority": "high", "tags": ["urgent"]}
            updated_conversation = service.update_conversation(
                conversation_id=1,
                metadata=new_metadata
            )

            # Verify the metadata was updated
            assert mock_conversation.metadata == new_metadata

            # Verify the session was committed and refreshed
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_conversation)

            assert updated_conversation == mock_conversation

    def test_update_conversation_status(self):
        """Test updating conversation active status."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock an existing conversation
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = 1
        mock_conversation.title = "Test Title"
        mock_conversation.user_id = 1
        mock_conversation.is_active = True

        # Mock the get_conversation_by_id method to return the conversation
        with patch.object(service, 'get_conversation_by_id', return_value=mock_conversation):
            updated_conversation = service.update_conversation_status(
                conversation_id=1,
                is_active=False
            )

            # Verify the status was updated
            assert mock_conversation.is_active is False

            # Verify the session was committed and refreshed
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_conversation)

            assert updated_conversation == mock_conversation

    def test_update_conversation_not_found(self):
        """Test updating a non-existent conversation."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the get_conversation_by_id method to return None
        with patch.object(service, 'get_conversation_by_id', return_value=None):
            result = service.update_conversation(
                conversation_id=999,
                title="Updated Title"
            )

            # Should return None if conversation not found
            assert result is None

            # Verify nothing was committed
            mock_db.commit.assert_not_called()


class TestConversationServiceConversationDeletion:
    """Tests for conversation deletion functionality."""

    def test_delete_conversation_success(self):
        """Test successfully deleting a conversation."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock an existing conversation
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = 1
        mock_conversation.title = "Delete Me"
        mock_conversation.user_id = 1

        # Mock the get_conversation_by_id method to return the conversation
        with patch.object(service, 'get_conversation_by_id', return_value=mock_conversation):
            result = service.delete_conversation(1)

            # Verify the conversation was deleted from the session
            mock_db.delete.assert_called_once_with(mock_conversation)
            mock_db.commit.assert_called_once()

            assert result is True

    def test_delete_conversation_not_found(self):
        """Test attempting to delete a non-existent conversation."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the get_conversation_by_id method to return None
        with patch.object(service, 'get_conversation_by_id', return_value=None):
            result = service.delete_conversation(999)

            # Verify nothing was deleted
            mock_db.delete.assert_not_called()
            mock_db.commit.assert_not_called()

            assert result is False

    def test_soft_delete_conversation(self):
        """Test soft deleting a conversation by setting it as inactive."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock an existing conversation
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = 1
        mock_conversation.title = "Soft Delete Me"
        mock_conversation.user_id = 1
        mock_conversation.is_active = True

        # Mock the get_conversation_by_id method to return the conversation
        with patch.object(service, 'get_conversation_by_id', return_value=mock_conversation):
            result = service.soft_delete_conversation(1)

            # Verify the conversation was marked as inactive
            assert mock_conversation.is_active is False

            # Verify the session was committed and refreshed
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_conversation)

            assert result is True


class TestConversationServiceMessageManagement:
    """Tests for message management within conversations."""

    def test_add_message_to_conversation(self):
        """Test adding a message to a conversation."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock an existing conversation
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = 1
        mock_conversation.title = "Test Conversation"
        mock_conversation.user_id = 1

        # Mock the get_conversation_by_id method to return the conversation
        with patch.object(service, 'get_conversation_by_id', return_value=mock_conversation):
            # Mock the message creation
            with patch('src.services.conversation_service.Message') as mock_message_class:
                mock_message = Mock(spec=Message)
                mock_message.id = 1
                mock_message.content = "Test message"
                mock_message.conversation_id = 1
                mock_message.sender_id = 1
                mock_message_class.return_value = mock_message

                result = service.add_message_to_conversation(
                    conversation_id=1,
                    content="Test message",
                    sender_id=1,
                    message_type="text"
                )

                # Verify the message was added to the session
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()

                # Verify the result
                assert result.content == "Test message"
                assert result.conversation_id == 1

    def test_get_messages_from_conversation(self):
        """Test retrieving messages from a conversation."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the query result
        mock_messages = [
            Mock(spec=Message, id=1, content="Message 1", conversation_id=1, sender_id=1),
            Mock(spec=Message, id=2, content="Message 2", conversation_id=1, sender_id=2)
        ]

        mock_query = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_filter  # For ordering by timestamp
        mock_filter.all.return_value = mock_messages

        result = service.get_messages_from_conversation(conversation_id=1)

        # Verify the query was constructed correctly
        mock_db.query.assert_called_once_with(Message)
        assert result == mock_messages

    def test_get_messages_from_conversation_with_pagination(self):
        """Test retrieving messages from a conversation with pagination."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the query result
        mock_messages = [
            Mock(spec=Message, id=1, content="Message 1", conversation_id=1, sender_id=1),
            Mock(spec=Message, id=2, content="Message 2", conversation_id=1, sender_id=2)
        ]

        mock_query = Mock()
        mock_filter = Mock()
        mock_order = Mock()
        mock_offset = Mock()
        mock_limit = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order
        mock_order.offset.return_value = mock_offset
        mock_offset.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_messages

        result = service.get_messages_from_conversation_paginated(
            conversation_id=1, skip=0, limit=10
        )

        # Verify the query was constructed with offset and limit
        mock_db.query.assert_called_once_with(Message)
        mock_filter.order_by.assert_called_once()  # Ordering by timestamp
        mock_order.offset.assert_called_once_with(0)
        mock_offset.limit.assert_called_once_with(10)
        assert result == mock_messages

    def test_get_latest_messages_from_conversation(self):
        """Test retrieving the latest messages from a conversation."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the query result
        mock_messages = [
            Mock(spec=Message, id=5, content="Latest Message", conversation_id=1, timestamp=datetime.now()),
            Mock(spec=Message, id=4, content="Older Message", conversation_id=1, timestamp=datetime.now() - timedelta(minutes=1))
        ]

        mock_query = Mock()
        mock_filter = Mock()
        mock_order = Mock()
        mock_limit = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order
        mock_order.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_messages

        result = service.get_latest_messages_from_conversation(
            conversation_id=1, limit=5
        )

        # Verify the query was constructed with limit and ordering
        mock_db.query.assert_called_once_with(Message)
        mock_filter.order_by.assert_called_once()  # Ordering by timestamp desc
        mock_order.limit.assert_called_once_with(5)
        assert result == mock_messages


class TestConversationServiceSearch:
    """Tests for conversation search functionality."""

    def test_search_conversations_by_title(self):
        """Test searching conversations by title."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the query result
        mock_conversations = [
            Mock(spec=Conversation, id=1, title="Support Ticket #123", user_id=1),
            Mock(spec=Conversation, id=2, title="Customer Support Query", user_id=1)
        ]

        mock_query = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = mock_conversations

        result = service.search_conversations_by_title(user_id=1, search_term="Support")

        # Verify the query was constructed with the search filter
        mock_db.query.assert_called_once_with(Conversation)
        assert result == mock_conversations

    def test_search_conversations_by_content(self):
        """Test searching conversations by content of messages."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the query result
        mock_conversations = [
            Mock(spec=Conversation, id=1, title="Conv with Important Info", user_id=1)
        ]

        mock_query = Mock()
        mock_join = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.join.return_value = mock_join
        mock_join.filter.return_value = mock_filter
        mock_filter.distinct.return_value = mock_filter
        mock_filter.all.return_value = mock_conversations

        result = service.search_conversations_by_content(user_id=1, search_term="important")

        # Verify the query was constructed with join and search filter
        mock_db.query.assert_called_once_with(Conversation)
        mock_query.join.assert_called_once_with(Message)
        assert result == mock_conversations


class TestConversationServiceStatistics:
    """Tests for conversation statistics functionality."""

    def test_get_user_conversation_stats(self):
        """Test getting user conversation statistics."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the query results for counting
        mock_active_count = Mock()
        mock_total_count = Mock()

        # Setting up the mock chain for counting queries
        mock_query1 = Mock()
        mock_query1.filter.return_value = Mock()
        mock_query1.filter.return_value.count.return_value = 5  # Active conversations

        mock_query2 = Mock()
        mock_query2.filter.return_value = Mock()
        mock_query2.filter.return_value.count.return_value = 10  # Total conversations

        mock_db.query = Mock(side_effect=[mock_query1, mock_query2])

        stats = service.get_user_conversation_stats(user_id=1)

        # Verify that the method returns the expected stats structure
        assert "total_conversations" in stats
        assert "active_conversations" in stats
        assert "recent_conversations" in stats

    def test_get_conversation_message_count(self):
        """Test getting the message count for a conversation."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the count query result
        mock_count_query = Mock()
        mock_filtered_query = Mock()

        mock_db.query.return_value = mock_count_query
        mock_count_query.filter.return_value = mock_filtered_query
        mock_filtered_query.count.return_value = 25

        count = service.get_conversation_message_count(conversation_id=1)

        # Verify the count was retrieved correctly
        mock_db.query.assert_called_once_with(Message)
        assert count == 25


class TestConversationServiceAccessControl:
    """Tests for conversation access control."""

    def test_user_owns_conversation_true(self):
        """Test that access control correctly identifies owned conversation."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock an existing conversation
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = 1
        mock_conversation.user_id = 123

        # Mock the get_conversation_by_id method to return the conversation
        with patch.object(service, 'get_conversation_by_id', return_value=mock_conversation):
            result = service.user_owns_conversation(user_id=123, conversation_id=1)

            assert result is True

    def test_user_owns_conversation_false(self):
        """Test that access control correctly identifies non-owned conversation."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock an existing conversation
        mock_conversation = Mock(spec=Conversation)
        mock_conversation.id = 1
        mock_conversation.user_id = 456  # Different user

        # Mock the get_conversation_by_id method to return the conversation
        with patch.object(service, 'get_conversation_by_id', return_value=mock_conversation):
            result = service.user_owns_conversation(user_id=123, conversation_id=1)

            assert result is False

    def test_user_owns_conversation_not_found(self):
        """Test access control for non-existent conversation."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the get_conversation_by_id method to return None
        with patch.object(service, 'get_conversation_by_id', return_value=None):
            result = service.user_owns_conversation(user_id=123, conversation_id=999)

            assert result is False


class TestConversationServiceUtilities:
    """Tests for conversation utility functions."""

    def test_generate_conversation_title(self):
        """Test generating a conversation title from first message."""
        service = ConversationService(Mock(spec=Session))

        first_message = "Hello, I need help with my account."
        generated_title = service.generate_conversation_title(first_message)

        # Verify the title is properly truncated if too long
        assert isinstance(generated_title, str)
        assert len(generated_title) <= 50  # Assuming 50 char limit
        assert "Hello" in generated_title

    def test_generate_conversation_title_short_message(self):
        """Test generating a title from a short message."""
        service = ConversationService(Mock(spec=Session))

        short_message = "Hi"
        generated_title = service.generate_conversation_title(short_message)

        # For very short messages, it might use a default
        assert isinstance(generated_title, str)

    def test_archive_old_conversations(self):
        """Test archiving conversations older than a certain date."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the query for old conversations
        mock_conversations = [
            Mock(spec=Conversation, id=1, title="Old Conv", user_id=1, is_active=True),
        ]

        mock_query = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = mock_conversations

        # Mock updating the conversations
        result = service.archive_conversations_older_than(days=30)

        # Verify the conversations were found and updated
        mock_db.query.assert_called_once_with(Conversation)
        # The method would update each conversation's is_active status
        mock_db.commit.assert_called_once()

    def test_get_conversations_by_date_range(self):
        """Test retrieving conversations within a date range."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # Mock the query result
        mock_conversations = [
            Mock(spec=Conversation, id=1, title="Date Range Conv", user_id=1)
        ]

        mock_query = Mock()
        mock_filter = Mock()
        mock_filter2 = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.filter.return_value = mock_filter2
        mock_filter2.all.return_value = mock_conversations

        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()

        result = service.get_conversations_by_date_range(
            user_id=1, start_date=start_date, end_date=end_date
        )

        # Verify the query was constructed with date filters
        mock_db.query.assert_called_once_with(Conversation)
        assert result == mock_conversations


class TestConversationServiceErrorHandling:
    """Tests for error handling in ConversationService."""

    def test_create_conversation_with_invalid_user(self):
        """Test creating a conversation with an invalid user ID."""
        mock_db = Mock(spec=Session)
        service = ConversationService(mock_db)

        # This would typically check if the user exists first
        # For now, testing that the service handles the database operation
        with patch('src.services.conversation_service.Conversation') as mock_conversation_class:
            instance = Mock()
            mock_conversation_class.return_value = instance

            # If the user doesn't exist, the foreign key constraint would fail
            mock_db.commit.side_effect = Exception("Foreign key violation")

            with pytest.raises(Exception, match="Foreign key violation"):
                service.create_conversation(
                    title="Test Conversation",
                    user_id=999999  # Non-existent user
                )