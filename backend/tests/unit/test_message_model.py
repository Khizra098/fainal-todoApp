"""
Unit tests for the Message model.

This module contains unit tests for the Message model including validation,
creation, relationships, and property access.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from src.models.message import Message
from src.models.conversation import Conversation
from src.models.user import User
from src.database.database import Base


@pytest.fixture
def test_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_user(test_db):
    """Create a sample user for testing relationships."""
    user = User(
        email="message.user@example.com",
        username="msguser",
        hashed_password="password"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def sample_conversation(test_db, sample_user):
    """Create a sample conversation for testing relationships."""
    conversation = Conversation(
        title="Test Conversation for Messages",
        user_id=sample_user.id
    )
    test_db.add(conversation)
    test_db.commit()
    test_db.refresh(conversation)
    return conversation


class TestMessageModelBasic:
    """Basic tests for the Message model."""

    def test_message_creation_with_valid_data(self, test_db, sample_user, sample_conversation):
        """Test creating a message with valid data."""
        message = Message(
            content="This is a test message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id,
            message_type="text"
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        assert message.content == "This is a test message"
        assert message.conversation_id == sample_conversation.id
        assert message.sender_id == sample_user.id
        assert message.message_type == "text"
        assert message.id is not None
        assert message.timestamp is not None

    def test_message_default_values(self, test_db, sample_user, sample_conversation):
        """Test default values for optional fields."""
        message = Message(
            content="Default Values Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        # Check default values
        assert message.content == "Default Values Message"
        assert message.conversation_id == sample_conversation.id
        assert message.sender_id == sample_user.id
        assert message.message_type == "text"  # Default message type
        assert message.is_read is False  # Default to not read
        assert message.metadata == {}  # Default to empty metadata
        assert message.parent_message_id is None  # Default to no parent

    def test_message_optional_fields(self, test_db, sample_user, sample_conversation):
        """Test setting optional fields."""
        metadata = {
            "reactions": ["like", "laugh"],
            "edited": True,
            "edit_time": datetime.utcnow().isoformat()
        }

        message = Message(
            content="Optional Fields Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id,
            message_type="text",
            is_read=True,
            metadata=metadata,
            parent_message_id=1
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        assert message.content == "Optional Fields Message"
        assert message.is_read is True
        assert message.metadata == metadata
        assert message.parent_message_id == 1

    def test_message_str_representation(self, test_db, sample_user, sample_conversation):
        """Test the string representation of the Message model."""
        message = Message(
            content="String Test Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        expected_str = f"Message(id={message.id}, conversation_id={sample_conversation.id}, sender_id={sample_user.id})"
        assert str(message) == expected_str

    def test_message_to_dict_method(self, test_db, sample_user, sample_conversation):
        """Test the to_dict method of the Message model."""
        metadata = {"reactions": ["like"], "edited": False}
        message = Message(
            content="Dict Test Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id,
            message_type="text",
            is_read=False,
            metadata=metadata
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        msg_dict = message.to_dict()

        assert "id" in msg_dict
        assert msg_dict["content"] == "Dict Test Message"
        assert msg_dict["conversation_id"] == sample_conversation.id
        assert msg_dict["sender_id"] == sample_user.id
        assert msg_dict["message_type"] == "text"
        assert msg_dict["is_read"] is False
        assert msg_dict["metadata"] == metadata
        assert "timestamp" in msg_dict


class TestMessageModelValidation:
    """Tests for Message model validation and constraints."""

    def test_message_content_length(self, test_db, sample_user, sample_conversation):
        """Test message content length validation."""
        long_content = "A" * 10000  # Assuming there's a length limit
        message = Message(
            content=long_content,
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        # Check if the content was truncated or if validation occurred
        assert message.content == long_content  # Or whatever the validation rule specifies

    def test_message_type_validation(self, test_db, sample_user, sample_conversation):
        """Test message type field validation."""
        valid_types = ["text", "image", "file", "audio", "video"]

        for msg_type in valid_types:
            message = Message(
                content=f"Message with {msg_type} type",
                conversation_id=sample_conversation.id,
                sender_id=sample_user.id,
                message_type=msg_type
            )

            test_db.add(message)
            test_db.commit()
            test_db.refresh(message)

            assert message.message_type == msg_type

    def test_message_relationships(self, test_db, sample_user, sample_conversation):
        """Test relationships with Conversation and User models."""
        message = Message(
            content="Relationship Test Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        assert message.conversation_id == sample_conversation.id
        assert message.sender_id == sample_user.id


class TestMessageModelTimestamps:
    """Tests for timestamp handling."""

    def test_timestamp_set_on_creation(self, test_db, sample_user, sample_conversation):
        """Test that timestamp is set when message is created."""
        before_creation = datetime.utcnow()

        message = Message(
            content="Timestamp Test Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        after_creation = datetime.utcnow()

        assert message.timestamp is not None
        assert before_creation <= message.timestamp <= after_creation

    def test_message_edit_timestamp(self, test_db, sample_user, sample_conversation):
        """Test that edit timestamp can be set."""
        message = Message(
            content="Editable Test Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        original_timestamp = message.timestamp

        # Simulate editing the message
        import time
        time.sleep(0.01)  # Small delay to ensure time difference

        edit_time = datetime.utcnow()
        message.edited_at = edit_time
        message.content = "Edited message content"
        test_db.commit()
        test_db.refresh(message)

        assert message.edited_at is not None
        assert message.edited_at >= edit_time
        assert message.content == "Edited message content"
        assert message.timestamp == original_timestamp  # Original timestamp unchanged


class TestMessageModelContentTypes:
    """Tests for different message content types."""

    def test_text_message(self, test_db, sample_user, sample_conversation):
        """Test creating a text message."""
        content = "This is a regular text message."
        message = Message(
            content=content,
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id,
            message_type="text"
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        assert message.content == content
        assert message.message_type == "text"

    def test_command_message(self, test_db, sample_user, sample_conversation):
        """Test creating a command message."""
        content = "/help show available commands"
        message = Message(
            content=content,
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id,
            message_type="command"
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        assert message.content == content
        assert message.message_type == "command"

    def test_system_message(self, test_db, sample_user, sample_conversation):
        """Test creating a system message."""
        content = "User joined the conversation"
        message = Message(
            content=content,
            conversation_id=sample_conversation.id,
            sender_id=None,  # System messages might not have a sender
            message_type="system"
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        assert message.content == content
        assert message.message_type == "system"
        assert message.sender_id is None


class TestMessageModelMetadata:
    """Tests for message metadata functionality."""

    def test_metadata_dictionary_storage(self, test_db, sample_user, sample_conversation):
        """Test storing and retrieving message metadata."""
        metadata = {
            "reactions": ["like", "love", "laugh"],
            "attachments": [
                {"type": "image", "url": "/path/to/image.jpg", "size": 102400},
                {"type": "file", "url": "/path/to/doc.pdf", "size": 2048000}
            ],
            "reply_to": {"message_id": 123, "preview": "Previous message content..."},
            "mentioned_users": [1, 2, 3],
            "is_edited": True,
            "thread_participants": [1, 2]
        }

        message = Message(
            content="Metadata Test Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id,
            metadata=metadata
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        assert message.metadata == metadata
        assert "like" in message.metadata["reactions"]
        assert len(message.metadata["attachments"]) == 2
        assert message.metadata["is_edited"] is True

    def test_metadata_default_empty(self, test_db, sample_user, sample_conversation):
        """Test that metadata defaults to empty dict."""
        message = Message(
            content="No Metadata Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        assert message.metadata == {}

    def test_metadata_can_be_updated(self, test_db, sample_user, sample_conversation):
        """Test updating message metadata."""
        message = Message(
            content="Update Metadata Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id,
            metadata={"initial": "value"}
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        # Update metadata
        message.metadata["reactions"] = ["like", "heart"]
        message.metadata["new_field"] = "new_value"
        test_db.commit()
        test_db.refresh(message)

        assert message.metadata["initial"] == "value"
        assert message.metadata["reactions"] == ["like", "heart"]
        assert message.metadata["new_field"] == "new_value"


class TestMessageModelReadStatus:
    """Tests for message read status functionality."""

    def test_is_read_flag(self, test_db, sample_user, sample_conversation):
        """Test the is_read flag."""
        unread_msg = Message(
            content="Unread Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id,
            is_read=False
        )

        read_msg = Message(
            content="Read Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id,
            is_read=True
        )

        test_db.add(unread_msg)
        test_db.add(read_msg)
        test_db.commit()

        test_db.refresh(unread_msg)
        test_db.refresh(read_msg)

        assert unread_msg.is_read is False
        assert read_msg.is_read is True

    def test_marking_message_as_read(self, test_db, sample_user, sample_conversation):
        """Test marking a message as read."""
        message = Message(
            content="Initially Unread Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id,
            is_read=False
        )

        test_db.add(message)
        test_db.commit()
        test_db.refresh(message)

        assert message.is_read is False

        # Mark as read
        message.is_read = True
        test_db.commit()
        test_db.refresh(message)

        assert message.is_read is True

    def test_bulk_read_status_update(self, test_db, sample_user, sample_conversation):
        """Test updating read status for multiple messages."""
        # Create multiple unread messages
        messages = []
        for i in range(5):
            msg = Message(
                content=f"Message {i}",
                conversation_id=sample_conversation.id,
                sender_id=sample_user.id,
                is_read=False
            )
            test_db.add(msg)
            messages.append(msg)

        test_db.commit()

        # Update all to read status
        for msg in messages:
            msg.is_read = True

        test_db.commit()

        # Verify all are now read
        for msg in messages:
            test_db.refresh(msg)
            assert msg.is_read is True


class TestMessageModelThreading:
    """Tests for message threading functionality."""

    def test_parent_message_relationship(self, test_db, sample_user, sample_conversation):
        """Test parent-child message relationships."""
        # Create a parent message
        parent_msg = Message(
            content="Parent message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id
        )

        test_db.add(parent_msg)
        test_db.commit()
        test_db.refresh(parent_msg)

        # Create a reply to the parent message
        reply_msg = Message(
            content="Reply to parent message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id,
            parent_message_id=parent_msg.id
        )

        test_db.add(reply_msg)
        test_db.commit()
        test_db.refresh(reply_msg)

        assert reply_msg.parent_message_id == parent_msg.id

    def test_nested_replies(self, test_db, sample_user, sample_conversation):
        """Test nested message replies."""
        # Create original message
        original_msg = Message(
            content="Original message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id
        )

        test_db.add(original_msg)
        test_db.commit()
        test_db.refresh(original_msg)

        # Create first reply
        reply_1 = Message(
            content="First reply",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id,
            parent_message_id=original_msg.id
        )

        test_db.add(reply_1)
        test_db.commit()
        test_db.refresh(reply_1)

        # Create reply to the first reply (nested reply)
        reply_2 = Message(
            content="Reply to first reply",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id,
            parent_message_id=reply_1.id  # Reply to the first reply
        )

        test_db.add(reply_2)
        test_db.commit()
        test_db.refresh(reply_2)

        assert reply_1.parent_message_id == original_msg.id
        assert reply_2.parent_message_id == reply_1.id


class TestMessageModelFilters:
    """Tests for message filtering methods."""

    def test_messages_by_conversation(self, test_db, sample_user, sample_conversation):
        """Test filtering messages by conversation."""
        # Create another conversation
        other_conv = Conversation(title="Other Conversation", user_id=sample_user.id)
        test_db.add(other_conv)
        test_db.commit()
        test_db.refresh(other_conv)

        # Create messages for first conversation
        msg1 = Message(content="Conv 1 Msg 1", conversation_id=sample_conversation.id, sender_id=sample_user.id)
        msg2 = Message(content="Conv 1 Msg 2", conversation_id=sample_conversation.id, sender_id=sample_user.id)

        # Create messages for other conversation
        msg3 = Message(content="Conv 2 Msg 1", conversation_id=other_conv.id, sender_id=sample_user.id)
        msg4 = Message(content="Conv 2 Msg 2", conversation_id=other_conv.id, sender_id=sample_user.id)

        test_db.add_all([msg1, msg2, msg3, msg4])
        test_db.commit()

        # Query messages for first conversation
        conv1_msgs = test_db.query(Message).filter(Message.conversation_id == sample_conversation.id).all()
        assert len(conv1_msgs) == 2
        contents = [msg.content for msg in conv1_msgs]
        assert "Conv 1 Msg 1" in contents
        assert "Conv 1 Msg 2" in contents
        assert "Conv 2 Msg 1" not in contents

    def test_messages_by_sender(self, test_db, sample_user, sample_conversation):
        """Test filtering messages by sender."""
        # Create another user
        other_user = User(email="other.msg@example.com", username="othermsguser", hashed_password="password")
        test_db.add(other_user)
        test_db.commit()
        test_db.refresh(other_user)

        # Create messages from different users
        msg1 = Message(content="User 1 Msg", conversation_id=sample_conversation.id, sender_id=sample_user.id)
        msg2 = Message(content="User 1 Another Msg", conversation_id=sample_conversation.id, sender_id=sample_user.id)
        msg3 = Message(content="User 2 Msg", conversation_id=sample_conversation.id, sender_id=other_user.id)

        test_db.add_all([msg1, msg2, msg3])
        test_db.commit()

        # Query messages from sample_user
        user1_msgs = test_db.query(Message).filter(Message.sender_id == sample_user.id).all()
        assert len(user1_msgs) == 2
        contents = [msg.content for msg in user1_msgs]
        assert "User 1 Msg" in contents
        assert "User 1 Another Msg" in contents
        assert "User 2 Msg" not in contents

    def test_messages_by_time_range(self, test_db, sample_user, sample_conversation):
        """Test filtering messages by time range."""
        # Create messages at different times
        past_time = datetime.utcnow() - timedelta(hours=2)
        current_time = datetime.utcnow()
        future_time = datetime.utcnow() + timedelta(hours=1)

        msg1 = Message(
            content="Past Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id
        )
        msg1.timestamp = past_time

        msg2 = Message(
            content="Current Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id
        )
        msg2.timestamp = current_time

        msg3 = Message(
            content="Future Message",
            conversation_id=sample_conversation.id,
            sender_id=sample_user.id
        )
        msg3.timestamp = future_time

        test_db.add_all([msg1, msg2, msg3])
        test_db.commit()

        # Query messages from past hour to future
        recent_msgs = test_db.query(Message).filter(
            Message.timestamp >= datetime.utcnow() - timedelta(hours=1)
        ).all()

        assert len(recent_msgs) >= 1  # At least the current message
        contents = [msg.content for msg in recent_msgs]
        if "Current Message" in [msg.content for msg in [msg1, msg2, msg3]]:
            assert "Current Message" in contents


class TestMessageModelSearch:
    """Tests for message search functionality."""

    def test_message_search_by_content(self, test_db, sample_user, sample_conversation):
        """Test searching messages by content."""
        msg1 = Message(content="Hello, how are you?", conversation_id=sample_conversation.id, sender_id=sample_user.id)
        msg2 = Message(content="I am fine, thank you!", conversation_id=sample_conversation.id, sender_id=sample_user.id)
        msg3 = Message(content="Let's discuss the project", conversation_id=sample_conversation.id, sender_id=sample_user.id)

        test_db.add_all([msg1, msg2, msg3])
        test_db.commit()

        # Search for messages containing "you"
        you_msgs = test_db.query(Message).filter(Message.content.contains("you")).all()

        assert len(you_msgs) == 2  # "how are you?" and "thank you!"
        contents = [msg.content for msg in you_msgs]
        assert "Hello, how are you?" in contents
        assert "I am fine, thank you!" in contents

    def test_case_insensitive_search(self, test_db, sample_user, sample_conversation):
        """Test case-insensitive message search."""
        msg1 = Message(content="HELLO world", conversation_id=sample_conversation.id, sender_id=sample_user.id)
        msg2 = Message(content="Hi Universe", conversation_id=sample_conversation.id, sender_id=sample_user.id)
        msg3 = Message(content="hello earth", conversation_id=sample_conversation.id, sender_id=sample_user.id)

        test_db.add_all([msg1, msg2, msg3])
        test_db.commit()

        # Search for "hello" in different cases
        hello_msgs = test_db.query(Message).filter(
            Message.content.ilike("%hello%")  # Case-insensitive LIKE
        ).all()

        assert len(hello_msgs) == 2  # "HELLO world" and "hello earth"
        contents = [msg.content for msg in hello_msgs]
        assert "HELLO world" in contents
        assert "hello earth" in contents


class TestMessageModelRelationships:
    """Tests for message relationships."""

    def test_message_id_generation(self, test_db, sample_user, sample_conversation):
        """Test that message IDs are properly generated."""
        msg1 = Message(content="ID Test 1", conversation_id=sample_conversation.id, sender_id=sample_user.id)
        msg2 = Message(content="ID Test 2", conversation_id=sample_conversation.id, sender_id=sample_user.id)

        test_db.add(msg1)
        test_db.add(msg2)
        test_db.commit()

        test_db.refresh(msg1)
        test_db.refresh(msg2)

        assert msg1.id is not None
        assert msg2.id is not None
        assert msg1.id != msg2.id

    def test_message_ordering_by_timestamp(self, test_db, sample_user, sample_conversation):
        """Test that messages can be ordered by timestamp."""
        import time

        msg1 = Message(content="First Message", conversation_id=sample_conversation.id, sender_id=sample_user.id)
        test_db.add(msg1)
        test_db.commit()
        test_db.refresh(msg1)

        time.sleep(0.01)  # Small delay to ensure different timestamps

        msg2 = Message(content="Second Message", conversation_id=sample_conversation.id, sender_id=sample_user.id)
        test_db.add(msg2)
        test_db.commit()
        test_db.refresh(msg2)

        time.sleep(0.01)  # Small delay to ensure different timestamps

        msg3 = Message(content="Third Message", conversation_id=sample_conversation.id, sender_id=sample_user.id)
        test_db.add(msg3)
        test_db.commit()
        test_db.refresh(msg3)

        # Query messages ordered by timestamp (ascending)
        ordered_msgs = test_db.query(Message).filter(
            Message.conversation_id == sample_conversation.id
        ).order_by(Message.timestamp).all()

        assert ordered_msgs[0].content == "First Message"
        assert ordered_msgs[1].content == "Second Message"
        assert ordered_msgs[2].content == "Third Message"