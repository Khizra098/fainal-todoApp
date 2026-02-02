"""
Unit tests for the User model.

This module contains unit tests for the User model including validation,
creation, relationships, and property access.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from passlib.context import CryptContext

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


class TestUserModelBasic:
    """Basic tests for the User model."""

    def test_user_creation_with_valid_data(self, test_db):
        """Test creating a user with valid data."""
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123"
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.hashed_password == "hashed_password_123"
        assert user.id is not None
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_default_values(self, test_db):
        """Test default values for optional fields."""
        user = User(
            email="defaults@example.com",
            username="defaultuser",
            hashed_password="password"
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Check default values
        assert user.is_active is True
        assert user.is_verified is False
        assert user.role == "user"
        assert user.preferences == {}
        assert user.failed_login_attempts == 0
        assert user.last_login_at is None

    def test_user_optional_fields(self, test_db):
        """Test setting optional fields."""
        preferences = {"theme": "dark", "notifications": True, "language": "en"}

        user = User(
            email="optional@example.com",
            username="optionaluser",
            hashed_password="password",
            is_active=False,
            is_verified=True,
            role="admin",
            preferences=preferences,
            failed_login_attempts=3,
            last_login_at=datetime.utcnow()
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.is_active is False
        assert user.is_verified is True
        assert user.role == "admin"
        assert user.preferences == preferences
        assert user.failed_login_attempts == 3
        assert user.last_login_at is not None

    def test_user_str_representation(self, test_db):
        """Test the string representation of the User model."""
        user = User(
            email="str@example.com",
            username="struser",
            hashed_password="password"
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        expected_str = f"User(id={user.id}, username='struser', email='str@example.com')"
        assert str(user) == expected_str

    def test_user_to_dict_method(self, test_db):
        """Test the to_dict method of the User model."""
        preferences = {"theme": "light"}
        user = User(
            email="dict@example.com",
            username="dictuser",
            hashed_password="password",
            is_active=True,
            preferences=preferences
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        user_dict = user.to_dict()

        assert "id" in user_dict
        assert user_dict["email"] == "dict@example.com"
        assert user_dict["username"] == "dictuser"
        assert user_dict["is_active"] is True
        assert user_dict["preferences"] == preferences
        assert "created_at" in user_dict
        assert "updated_at" in user_dict

        # Ensure sensitive data is not included
        assert "hashed_password" not in user_dict


class TestUserModelValidation:
    """Tests for User model validation and constraints."""

    def test_user_email_uniqueness(self, test_db):
        """Test that email addresses must be unique."""
        # Create first user
        user1 = User(
            email="unique@example.com",
            username="user1",
            hashed_password="password1"
        )
        test_db.add(user1)
        test_db.commit()

        # Try to create second user with same email
        user2 = User(
            email="unique@example.com",  # Same email as user1
            username="user2",
            hashed_password="password2"
        )
        test_db.add(user2)

        # This should raise an exception due to unique constraint
        with pytest.raises(Exception):  # Could be IntegrityError or other DB exception
            test_db.commit()

    def test_user_username_uniqueness(self, test_db):
        """Test that usernames must be unique."""
        # Create first user
        user1 = User(
            email="unique1@example.com",
            username="sameusername",
            hashed_password="password1"
        )
        test_db.add(user1)
        test_db.commit()

        # Try to create second user with same username
        user2 = User(
            email="unique2@example.com",
            username="sameusername",  # Same username as user1
            hashed_password="password2"
        )
        test_db.add(user2)

        # This should raise an exception due to unique constraint
        with pytest.raises(Exception):  # Could be IntegrityError or other DB exception
            test_db.commit()

    def test_user_email_format(self, test_db):
        """Test email format validation."""
        # Test with a valid email format
        user = User(
            email="valid.format@example.com",
            username="validemail",
            hashed_password="password"
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.email == "valid.format@example.com"

    def test_user_role_validation(self, test_db):
        """Test that role field accepts valid values."""
        valid_roles = ["user", "admin", "moderator", "guest"]

        for role in valid_roles:
            user = User(
                email=f"{role}@example.com",
                username=f"user_{role}",
                hashed_password="password",
                role=role
            )
            test_db.add(user)
            test_db.commit()
            test_db.refresh(user)

            assert user.role == role


class TestUserModelPasswordHandling:
    """Tests for password-related functionality."""

    def test_password_hash_stored_correctly(self, test_db):
        """Test that password hash is stored correctly."""
        plain_password = "mysecretpassword"
        hashed_password = "$2b$12$LQZ4bsdWJl6DHl2Db.HODeLGzG2q/KqLQvaa6a00xHDcKsiyAC8bC"  # Example bcrypt hash

        user = User(
            email="password@example.com",
            username="passworduser",
            hashed_password=hashed_password
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.hashed_password == hashed_password
        # Note: We can't verify the actual password hashing here without the hashing function


class TestUserModelTimestamps:
    """Tests for timestamp handling."""

    def test_created_at_set_on_creation(self, test_db):
        """Test that created_at is set when user is created."""
        before_creation = datetime.utcnow()

        user = User(
            email="timestamp@example.com",
            username="timestampuser",
            hashed_password="password"
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        after_creation = datetime.utcnow()

        assert user.created_at is not None
        assert before_creation <= user.created_at <= after_creation

    def test_updated_at_changes_on_update(self, test_db):
        """Test that updated_at changes when user is updated."""
        user = User(
            email="update@example.com",
            username="updateuser",
            hashed_password="password"
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        original_updated_at = user.updated_at

        # Wait a moment to ensure time difference
        import time
        time.sleep(0.01)

        # Update the user
        user.username = "updated_username"
        test_db.commit()
        test_db.refresh(user)

        # updated_at should be different and later than original
        assert user.updated_at > original_updated_at
        assert user.username == "updated_username"

    def test_last_login_at_updates_properly(self, test_db):
        """Test that last_login_at can be updated."""
        user = User(
            email="login@example.com",
            username="loginuser",
            hashed_password="password"
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.last_login_at is None

        # Simulate a login by updating last_login_at
        login_time = datetime.utcnow()
        user.last_login_at = login_time
        test_db.commit()
        test_db.refresh(user)

        assert user.last_login_at == login_time


class TestUserModelPreferences:
    """Tests for user preferences functionality."""

    def test_preferences_dictionary_storage(self, test_db):
        """Test storing and retrieving user preferences."""
        preferences = {
            "theme": "dark",
            "notifications": {
                "email": True,
                "push": False
            },
            "privacy": {
                "profile_visible": True,
                "show_email": False
            }
        }

        user = User(
            email="prefs@example.com",
            username="prefsuser",
            hashed_password="password",
            preferences=preferences
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.preferences == preferences
        assert user.preferences["theme"] == "dark"
        assert user.preferences["notifications"]["email"] is True

    def test_preferences_default_empty(self, test_db):
        """Test that preferences defaults to empty dict."""
        user = User(
            email="noprefs@example.com",
            username="noprefsuser",
            hashed_password="password"
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.preferences == {}

    def test_preferences_can_be_updated(self, test_db):
        """Test updating user preferences."""
        user = User(
            email="updateprefs@example.com",
            username="updateprefsuser",
            hashed_password="password",
            preferences={"theme": "light"}
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Update preferences
        user.preferences["language"] = "en"
        user.preferences["notifications"] = True
        test_db.commit()
        test_db.refresh(user)

        assert user.preferences["theme"] == "light"
        assert user.preferences["language"] == "en"
        assert user.preferences["notifications"] is True


class TestUserModelStatusAndSecurity:
    """Tests for user status and security fields."""

    def test_is_active_flag(self, test_db):
        """Test the is_active flag."""
        active_user = User(
            email="active@example.com",
            username="activeuser",
            hashed_password="password",
            is_active=True
        )

        inactive_user = User(
            email="inactive@example.com",
            username="inactiveuser",
            hashed_password="password",
            is_active=False
        )

        test_db.add(active_user)
        test_db.add(inactive_user)
        test_db.commit()

        test_db.refresh(active_user)
        test_db.refresh(inactive_user)

        assert active_user.is_active is True
        assert inactive_user.is_active is False

    def test_is_verified_flag(self, test_db):
        """Test the is_verified flag."""
        verified_user = User(
            email="verified@example.com",
            username="verifieduser",
            hashed_password="password",
            is_verified=True
        )

        unverified_user = User(
            email="unverified@example.com",
            username="unverifieduser",
            hashed_password="password",
            is_verified=False
        )

        test_db.add(verified_user)
        test_db.add(unverified_user)
        test_db.commit()

        test_db.refresh(verified_user)
        test_db.refresh(unverified_user)

        assert verified_user.is_verified is True
        assert unverified_user.is_verified is False

    def test_failed_login_attempts_tracking(self, test_db):
        """Test tracking failed login attempts."""
        user = User(
            email="attempts@example.com",
            username="attemptsuser",
            hashed_password="password",
            failed_login_attempts=5
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        assert user.failed_login_attempts == 5

        # Increment failed attempts
        user.failed_login_attempts += 1
        test_db.commit()
        test_db.refresh(user)

        assert user.failed_login_attempts == 6

    def test_account_lockout_logic_simulation(self, test_db):
        """Test account lockout based on failed attempts (logic simulation)."""
        user = User(
            email="lockout@example.com",
            username="lockoutuser",
            hashed_password="password",
            failed_login_attempts=0
        )

        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Simulate multiple failed login attempts
        max_attempts = 5
        for i in range(max_attempts):
            user.failed_login_attempts += 1
            test_db.commit()
            test_db.refresh(user)

        # Check if account would be considered locked
        is_locked = user.failed_login_attempts >= max_attempts
        assert is_locked is True
        assert user.failed_login_attempts == max_attempts


class TestUserModelRelationships:
    """Tests for user relationships (if any are defined)."""

    # Note: The actual relationships would depend on how they're defined in the model
    # This is a placeholder for when relationships are added

    def test_user_id_generation(self, test_db):
        """Test that user IDs are properly generated."""
        user1 = User(
            email="id1@example.com",
            username="id1user",
            hashed_password="password"
        )

        user2 = User(
            email="id2@example.com",
            username="id2user",
            hashed_password="password"
        )

        test_db.add(user1)
        test_db.add(user2)
        test_db.commit()

        test_db.refresh(user1)
        test_db.refresh(user2)

        assert user1.id is not None
        assert user2.id is not None
        assert user1.id != user2.id