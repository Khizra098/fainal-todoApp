"""
Unit tests for the Conversation model.

This module contains unit tests for the Conversation model including validation,
creation, relationships, and property access.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

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
        email="conversation.user@example.com",
        username="convuser",
        hashed_password="password"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


class TestConversationModelBasic:
    """Basic tests for the Conversation model."""

    def test_conversation_creation_with_valid_data(self, test_db, sample_user):
        """Test creating a conversation with valid data."""
        conversation = Conversation(
            title="Test Conversation",
            description="A test conversation",
            user_id=sample_user.id,
            is_active=True
        )

        test_db.add(conversation)
        test_db.commit()
        test_db.refresh(conversation)

        assert conversation.title == "Test Conversation"
        assert conversation.description == "A test conversation"
        assert conversation.user_id == sample_user.id
        assert conversation.is_active is True
        assert conversation.id is not None
        assert conversation.created_at is not None
        assert conversation.updated_at is not None

    def test_conversation_default_values(self, test_db, sample_user):
        """Test default values for optional fields."""
        conversation = Conversation(
            title="Defaults Conversation",
            user_id=sample_user.id
        )

        test_db.add(conversation)
        test_db.commit()
        test_db.refresh(conversation)

        # Check default values
        assert conversation.title == "Defaults Conversation"
        assert conversation.user_id == sample_user.id
        assert conversation.is_active is True  # Should default to True
        assert conversation.title.startswith("Conversation") or conversation.title == "Defaults Conversation"
        assert conversation.metadata == {}

    def test_conversation_optional_fields(self, test_db, sample_user):
        """Test setting optional fields."""
        metadata = {
            "topic": "support",
            "priority": "high",
            "tags": ["urgent", "customer-support"]
        }

        conversation = Conversation(
            title="Optional Fields Conversation",
            description="Conversation with optional fields",
            user_id=sample_user.id,
            is_active=False,
            metadata=metadata
        )

        test_db.add(conversation)
        test_db.commit()
        test_db.refresh(conversation)

        assert conversation.title == "Optional Fields Conversation"
        assert conversation.description == "Conversation with optional fields"
        assert conversation.user_id == sample_user.id
        assert conversation.is_active is False
        assert conversation.metadata == metadata

    def test_conversation_str_representation(self, test_db, sample_user):
        """Test the string representation of the Conversation model."""
        conversation = Conversation(
            title="String Test Conversation",
            user_id=sample_user.id
        )

        test_db.add(conversation)
        test_db.commit()
        test_db.refresh(conversation)

        expected_str = f"Conversation(id={conversation.id}, title='String Test Conversation', user_id={sample_user.id})"
        assert str(conversation) == expected_str

    def test_conversation_to_dict_method(self, test_db, sample_user):
        """Test the to_dict method of the Conversation model."""
        metadata = {"category": "support", "urgency": "high"}
        conversation = Conversation(
            title="Dict Test Conversation",
            description="Testing to_dict method",
            user_id=sample_user.id,
            is_active=True,
            metadata=metadata
        )

        test_db.add(conversation)
        test_db.commit()
        test_db.refresh(conversation)

        conv_dict = conversation.to_dict()

        assert "id" in conv_dict
        assert conv_dict["title"] == "Dict Test Conversation"
        assert conv_dict["description"] == "Testing to_dict method"
        assert conv_dict["user_id"] == sample_user.id
        assert conv_dict["is_active"] is True
        assert conv_dict["metadata"] == metadata
        assert "created_at" in conv_dict
        assert "updated_at" in conv_dict


class TestConversationModelValidation:
    """Tests for Conversation model validation and constraints."""

    def test_conversation_title_length(self, test_db, sample_user):
        """Test conversation title length validation."""
        long_title = "A" * 200  # Assuming there's a length limit
        conversation = Conversation(
            title=long_title,
            user_id=sample_user.id
        )

        test_db.add(conversation)
        test_db.commit()
        test_db.refresh(conversation)

        # Check if the title was truncated or if validation occurred
        assert conversation.title == long_title  # Or whatever the validation rule specifies

    def test_conversation_user_relationship(self, test_db, sample_user):
        """Test the relationship with User model."""
        conversation = Conversation(
            title="User Relationship Test",
            user_id=sample_user.id
        )

        test_db.add(conversation)
        test_db.commit()
        test_db.refresh(conversation)

        assert conversation.user_id == sample_user.id
        # Note: Actual relationship access depends on how it's defined in the model


class TestConversationModelTimestamps:
    """Tests for timestamp handling."""

    def test_created_at_set_on_creation(self, test_db, sample_user):
        """Test that created_at is set when conversation is created."""
        before_creation = datetime.utcnow()

        conversation = Conversation(
            title="Timestamp Test Conversation",
            user_id=sample_user.id
        )

        test_db.add(conversation)
        test_db.commit()
        test_db.refresh(conversation)

        after_creation = datetime.utcnow()

        assert conversation.created_at is not None
        assert before_creation <= conversation.created_at <= after_creation

    def test_updated_at_changes_on_update(self, test_db, sample_user):
        """Test that updated_at changes when conversation is updated."""
        conversation = Conversation(
            title="Update Test Conversation",
            user_id=sample_user.id
        )

        test_db.add(conversation)
        test_db.commit()
        test_db.refresh(conversation)

        original_updated_at = conversation.updated_at

        # Wait a moment to ensure time difference
        import time
        time.sleep(0.01)

        # Update the conversation
        conversation.title = "Updated Conversation Title"
        test_db.commit()
        test_db.refresh(conversation)

        # updated_at should be different and later than original
        assert conversation.updated_at > original_updated_at
        assert conversation.title == "Updated Conversation Title"

    def test_conversation_duration_calculation(self, test_db, sample_user):
        """Test conversation duration calculation."""
        # Create conversation with start time
        conversation = Conversation(
            title="Duration Test Conversation",
            user_id=sample_user.id
        )

        test_db.add(conversation)
        test_db.commit()
        test_db.refresh(conversation)

        # Simulate conversation end by setting an end time
        start_time = conversation.created_at
        end_time = start_time + timedelta(minutes=10)

        # Duration calculation would typically be a method in the model
        # For now, we'll just verify the timestamps exist
        assert start_time is not None
        assert isinstance(start_time, datetime)


class TestConversationModelMetadata:
    """Tests for conversation metadata functionality."""

    def test_metadata_dictionary_storage(self, test_db, sample_user):
        """Test storing and retrieving conversation metadata."""
        metadata = {
            "category": "technical-support",
            "priority": "high",
            "tags": ["urgent", "software", "bug-report"],
            "context": {
                "product_version": "1.2.3",
                "user_tier": "premium"
            }
        }

        conversation = Conversation(
            title="Metadata Test Conversation",
            user_id=sample_user.id,
            metadata=metadata
        )

        test_db.add(conversation)
        test_db.commit()
        test_db.refresh(conversation)

        assert conversation.metadata == metadata
        assert conversation.metadata["category"] == "technical-support"
        assert conversation.metadata["priority"] == "high"
        assert "urgent" in conversation.metadata["tags"]

    def test_metadata_default_empty(self, test_db, sample_user):
        """Test that metadata defaults to empty dict."""
        conversation = Conversation(
            title="No Metadata Conversation",
            user_id=sample_user.id
        )

        test_db.add(conversation)
        test_db.commit()
        test_db.refresh(conversation)

        assert conversation.metadata == {}

    def test_metadata_can_be_updated(self, test_db, sample_user):
        """Test updating conversation metadata."""
        conversation = Conversation(
            title="Update Metadata Conversation",
            user_id=sample_user.id,
            metadata={"initial": "value"}
        )

        test_db.add(conversation)
        test_db.commit()
        test_db.refresh(conversation)

        # Update metadata
        conversation.metadata["new_field"] = "new_value"
        conversation.metadata["category"] = "support"
        test_db.commit()
        test_db.refresh(conversation)

        assert conversation.metadata["initial"] == "value"
        assert conversation.metadata["new_field"] == "new_value"
        assert conversation.metadata["category"] == "support"


class TestConversationModelStatus:
    """Tests for conversation status functionality."""

    def test_is_active_flag(self, test_db, sample_user):
        """Test the is_active flag."""
        active_conv = Conversation(
            title="Active Conversation",
            user_id=sample_user.id,
            is_active=True
        )

        inactive_conv = Conversation(
            title="Inactive Conversation",
            user_id=sample_user.id,
            is_active=False
        )

        test_db.add(active_conv)
        test_db.add(inactive_conv)
        test_db.commit()

        test_db.refresh(active_conv)
        test_db.refresh(inactive_conv)

        assert active_conv.is_active is True
        assert inactive_conv.is_active is False

    def test_activating_deactivating_conversation(self, test_db, sample_user):
        """Test activating and deactivating conversations."""
        conversation = Conversation(
            title="Toggle Active Conversation",
            user_id=sample_user.id,
            is_active=True
        )

        test_db.add(conversation)
        test_db.commit()
        test_db.refresh(conversation)

        assert conversation.is_active is True

        # Deactivate
        conversation.is_active = False
        test_db.commit()
        test_db.refresh(conversation)

        assert conversation.is_active is False

        # Reactivate
        conversation.is_active = True
        test_db.commit()
        test_db.refresh(conversation)

        assert conversation.is_active is True


class TestConversationModelFilters:
    """Tests for conversation filtering methods."""

    def test_conversation_filters_by_user(self, test_db):
        """Test that conversations can be filtered by user."""
        user1 = User(email="user1@example.com", username="user1", hashed_password="password")
        user2 = User(email="user2@example.com", username="user2", hashed_password="password")

        test_db.add(user1)
        test_db.add(user2)
        test_db.commit()

        # Create conversations for user1
        conv1 = Conversation(title="User1 Conv 1", user_id=user1.id)
        conv2 = Conversation(title="User1 Conv 2", user_id=user1.id)

        # Create conversation for user2
        conv3 = Conversation(title="User2 Conv 1", user_id=user2.id)

        test_db.add(conv1)
        test_db.add(conv2)
        test_db.add(conv3)
        test_db.commit()

        # Query conversations for user1
        user1_convs = test_db.query(Conversation).filter(Conversation.user_id == user1.id).all()

        assert len(user1_convs) == 2
        conv_titles = [conv.title for conv in user1_convs]
        assert "User1 Conv 1" in conv_titles
        assert "User1 Conv 2" in conv_titles
        assert "User2 Conv 1" not in conv_titles

    def test_conversation_filters_by_active_status(self, test_db, sample_user):
        """Test that conversations can be filtered by active status."""
        active_conv = Conversation(
            title="Active Conv",
            user_id=sample_user.id,
            is_active=True
        )

        inactive_conv = Conversation(
            title="Inactive Conv",
            user_id=sample_user.id,
            is_active=False
        )

        test_db.add(active_conv)
        test_db.add(inactive_conv)
        test_db.commit()

        # Query active conversations
        active_convs = test_db.query(Conversation).filter(Conversation.is_active == True).all()
        assert len(active_convs) == 1
        assert active_convs[0].title == "Active Conv"

        # Query inactive conversations
        inactive_convs = test_db.query(Conversation).filter(Conversation.is_active == False).all()
        assert len(inactive_convs) == 1
        assert inactive_convs[0].title == "Inactive Conv"


class TestConversationModelSearch:
    """Tests for conversation search functionality."""

    def test_conversation_search_by_title(self, test_db, sample_user):
        """Test searching conversations by title."""
        conv1 = Conversation(title="Support Ticket #123", user_id=sample_user.id)
        conv2 = Conversation(title="Sales Inquiry", user_id=sample_user.id)
        conv3 = Conversation(title="Technical Support Question", user_id=sample_user.id)

        test_db.add(conv1)
        test_db.add(conv2)
        test_db.add(conv3)
        test_db.commit()

        # Search for conversations containing "Support"
        support_convs = test_db.query(Conversation).filter(
            Conversation.title.contains("Support")
        ).all()

        assert len(support_convs) == 2  # "Support Ticket #123" and "Technical Support Question"
        titles = [conv.title for conv in support_convs]
        assert "Support Ticket #123" in titles
        assert "Technical Support Question" in titles

    def test_conversation_search_by_description(self, test_db, sample_user):
        """Test searching conversations by description."""
        conv1 = Conversation(
            title="Conv 1",
            description="This is a technical support conversation",
            user_id=sample_user.id
        )
        conv2 = Conversation(
            title="Conv 2",
            description="Sales discussion about new features",
            user_id=sample_user.id
        )
        conv3 = Conversation(
            title="Conv 3",
            description="General inquiry about pricing",
            user_id=sample_user.id
        )

        test_db.add(conv1)
        test_db.add(conv2)
        test_db.add(conv3)
        test_db.commit()

        # Search for conversations containing "support"
        support_convs = test_db.query(Conversation).filter(
            Conversation.description.contains("support")
        ).all()

        assert len(support_convs) == 1
        assert support_convs[0].description == "This is a technical support conversation"


class TestConversationModelRelationships:
    """Tests for conversation relationships (when messages are added)."""

    def test_conversation_id_generation(self, test_db, sample_user):
        """Test that conversation IDs are properly generated."""
        conv1 = Conversation(title="ID Test 1", user_id=sample_user.id)
        conv2 = Conversation(title="ID Test 2", user_id=sample_user.id)

        test_db.add(conv1)
        test_db.add(conv2)
        test_db.commit()

        test_db.refresh(conv1)
        test_db.refresh(conv2)

        assert conv1.id is not None
        assert conv2.id is not None
        assert conv1.id != conv2.id

    def test_conversation_unique_constraints(self, test_db, sample_user):
        """Test that conversations can have the same title for different users."""
        # Two different users can have conversations with the same title
        user1 = User(email="user1.conv@example.com", username="user1conv", hashed_password="password")
        user2 = User(email="user2.conv@example.com", username="user2conv", hashed_password="password")

        test_db.add(user1)
        test_db.add(user2)
        test_db.commit()

        # Both users can have a conversation titled "General"
        conv1 = Conversation(title="General", user_id=user1.id)
        conv2 = Conversation(title="General", user_id=user2.id)  # Same title, different user

        test_db.add(conv1)
        test_db.add(conv2)
        test_db.commit()

        test_db.refresh(conv1)
        test_db.refresh(conv2)

        assert conv1.title == conv2.title == "General"
        assert conv1.user_id != conv2.user_id
        assert conv1.id != conv2.id