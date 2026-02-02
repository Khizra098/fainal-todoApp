"""
Unit tests for the UserService.

This module contains unit tests for the UserService class including validation,
business logic, and data access operations.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.services.user_service import UserService
from src.models.user import User


class TestUserServiceBasic:
    """Basic tests for the UserService."""

    def test_user_service_initialization(self):
        """Test initializing UserService with a database session."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        assert service.db == mock_db

    def test_password_hashing_utility(self):
        """Test that password hashing utility works correctly."""
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        plain_password = "testpassword123"
        hashed = pwd_context.hash(plain_password)

        # Verify the password can be verified
        assert pwd_context.verify(plain_password, hashed) is True

        # Verify wrong password fails
        assert pwd_context.verify("wrongpassword", hashed) is False


class TestUserServiceUserCreation:
    """Tests for user creation functionality."""

    @patch('src.services.user_service.pwd_context')
    def test_create_user_with_valid_data(self, mock_pwd_context):
        """Test creating a user with valid data."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock password hashing
        mock_pwd_context.hash.return_value = "hashed_password_123"

        # Mock the user creation
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.username = "testuser"

        # Configure the mock to return the user when added
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        # Since we can't instantiate a real User without the full model,
        # we'll test the service method logic
        with patch('src.services.user_service.User') as mock_user_class:
            instance = Mock()
            instance.id = 1
            instance.email = "test@example.com"
            instance.username = "testuser"
            instance.hashed_password = "hashed_password_123"
            mock_user_class.return_value = instance

            result = service.create_user(
                email="test@example.com",
                username="testuser",
                password="testpassword123"
            )

            # Verify the password was hashed
            mock_pwd_context.hash.assert_called_once_with("testpassword123")

            # Verify the user was added to the session
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()

            # Verify the result
            assert result.email == "test@example.com"
            assert result.username == "testuser"

    @patch('src.services.user_service.pwd_context')
    def test_create_user_duplicate_email(self, mock_pwd_context):
        """Test creating a user with duplicate email raises exception."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock password hashing
        mock_pwd_context.hash.return_value = "hashed_password_123"

        # Mock the database to raise an exception for duplicate email
        mock_db.commit.side_effect = Exception("Duplicate email")

        with pytest.raises(Exception, match="Duplicate email"):
            service.create_user(
                email="duplicate@example.com",
                username="testuser1",
                password="password123"
            )

    @patch('src.services.user_service.pwd_context')
    def test_create_user_duplicate_username(self, mock_pwd_context):
        """Test creating a user with duplicate username raises exception."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock password hashing
        mock_pwd_context.hash.return_value = "hashed_password_123"

        # Mock the database to raise an exception for duplicate username
        mock_db.commit.side_effect = Exception("Duplicate username")

        with pytest.raises(Exception, match="Duplicate username"):
            service.create_user(
                email="unique@example.com",
                username="duplicate_username",
                password="password123"
            )


class TestUserServiceUserRetrieval:
    """Tests for user retrieval functionality."""

    def test_get_user_by_id(self):
        """Test retrieving a user by ID."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock the query result
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "found@example.com"
        mock_user.username = "founduser"

        mock_query = Mock()
        mock_filter = Mock()
        mock_first = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_user

        result = service.get_user_by_id(1)

        # Verify the query was constructed correctly
        mock_db.query.assert_called_once_with(User)
        # Note: The exact filter call depends on the actual implementation
        # This assumes the filter uses User.id == user_id
        assert result == mock_user

    def test_get_user_by_id_not_found(self):
        """Test retrieving a non-existent user by ID returns None."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock the query result to return None
        mock_query = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        result = service.get_user_by_id(999)

        assert result is None

    def test_get_user_by_email(self):
        """Test retrieving a user by email."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock the query result
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "lookup@example.com"
        mock_user.username = "lookupuser"

        mock_query = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_user

        result = service.get_user_by_email("lookup@example.com")

        # Verify the query was constructed correctly
        mock_db.query.assert_called_once_with(User)
        assert result == mock_user

    def test_get_user_by_email_not_found(self):
        """Test retrieving a non-existent user by email returns None."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock the query result to return None
        mock_query = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        result = service.get_user_by_email("nonexistent@example.com")

        assert result is None

    def test_get_user_by_username(self):
        """Test retrieving a user by username."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock the query result
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "username@example.com"
        mock_user.username = "targetuser"

        mock_query = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_user

        result = service.get_user_by_username("targetuser")

        # Verify the query was constructed correctly
        mock_db.query.assert_called_once_with(User)
        assert result == mock_user

    def test_get_user_by_username_not_found(self):
        """Test retrieving a non-existent user by username returns None."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock the query result to return None
        mock_query = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        result = service.get_user_by_username("nonexistent_user")

        assert result is None


class TestUserServiceAuthentication:
    """Tests for user authentication functionality."""

    @patch('src.services.user_service.pwd_context')
    def test_authenticate_user_success(self, mock_pwd_context):
        """Test successful user authentication."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock an existing user with a hashed password
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "auth@example.com"
        mock_user.username = "authuser"
        mock_user.hashed_password = "$2b$12$LQZ4bsdWJl6DHl2Db.HODeLGzG2q/KqLQvaa6a00xHDcKsiyAC8bC"  # bcrypt hash

        # Mock the query to return the user
        mock_query = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_user

        # Mock password verification to return True
        mock_pwd_context.verify.return_value = True

        result = service.authenticate_user("auth@example.com", "correctpassword")

        assert result == mock_user
        mock_pwd_context.verify.assert_called_once_with("correctpassword", mock_user.hashed_password)

    @patch('src.services.user_service.pwd_context')
    def test_authenticate_user_wrong_password(self, mock_pwd_context):
        """Test authentication fails with wrong password."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock an existing user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "auth@example.com"
        mock_user.username = "authuser"
        mock_user.hashed_password = "$2b$12$LQZ4bsdWJl6DHl2Db.HODeLGzG2q/KqLQvaa6a00xHDcKsiyAC8bC"

        # Mock the query to return the user
        mock_query = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_user

        # Mock password verification to return False
        mock_pwd_context.verify.return_value = False

        result = service.authenticate_user("auth@example.com", "wrongpassword")

        assert result is None
        mock_pwd_context.verify.assert_called_once_with("wrongpassword", mock_user.hashed_password)

    @patch('src.services.user_service.pwd_context')
    def test_authenticate_user_nonexistent_email(self, mock_pwd_context):
        """Test authentication fails with non-existent email."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock the query to return None (no user found)
        mock_query = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        result = service.authenticate_user("nonexistent@example.com", "anypassword")

        assert result is None
        # Password verification should not be called if user doesn't exist
        mock_pwd_context.verify.assert_not_called()

    @patch('src.services.user_service.pwd_context')
    def test_verify_password(self, mock_pwd_context):
        """Test the verify_password utility method."""
        mock_pwd_context.verify.return_value = True

        result = UserService.verify_password("plaintext", "hash")

        assert result is True
        mock_pwd_context.verify.assert_called_once_with("plaintext", "hash")


class TestUserServiceUserUpdates:
    """Tests for user update functionality."""

    def test_update_user_profile(self):
        """Test updating user profile information."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock an existing user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "original@example.com"
        mock_user.username = "originaluser"
        mock_user.full_name = "Original Name"

        # Mock the get_user_by_id method to return the user
        with patch.object(service, 'get_user_by_id', return_value=mock_user):
            updated_user = service.update_user_profile(
                user_id=1,
                full_name="Updated Name",
                bio="Updated bio"
            )

            # Verify the user attributes were updated
            assert mock_user.full_name == "Updated Name"
            assert mock_user.bio == "Updated bio"

            # Verify the session was committed and refreshed
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_user)

            assert updated_user == mock_user

    def test_update_user_profile_not_found(self):
        """Test updating profile for non-existent user."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock the get_user_by_id method to return None
        with patch.object(service, 'get_user_by_id', return_value=None):
            result = service.update_user_profile(
                user_id=999,
                full_name="Updated Name"
            )

            # Should return None if user not found
            assert result is None

            # Verify nothing was committed
            mock_db.commit.assert_not_called()

    def test_update_user_preferences(self):
        """Test updating user preferences."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock an existing user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "pref@example.com"
        mock_user.username = "prefuser"
        mock_user.preferences = {"theme": "light", "notifications": True}

        # Mock the get_user_by_id method to return the user
        with patch.object(service, 'get_user_by_id', return_value=mock_user):
            updated_prefs = {"theme": "dark", "language": "en", "notifications": False}
            updated_user = service.update_user_preferences(
                user_id=1,
                preferences=updated_prefs
            )

            # Verify the preferences were updated
            assert mock_user.preferences == updated_prefs

            # Verify the session was committed and refreshed
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_user)

            assert updated_user == mock_user

    def test_update_user_activity(self):
        """Test updating user activity timestamps."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock an existing user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "activity@example.com"
        mock_user.last_login_at = datetime.utcnow() - timedelta(days=1)

        # Mock the get_user_by_id method to return the user
        with patch.object(service, 'get_user_by_id', return_value=mock_user):
            result = service.update_last_login(1)

            # Verify the last_login_at was updated
            assert mock_user.last_login_at is not None

            # Verify the session was committed and refreshed
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_user)

            assert result == mock_user


class TestUserServiceUserDeletion:
    """Tests for user deletion functionality."""

    def test_delete_user_success(self):
        """Test successfully deleting a user."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock an existing user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "delete@example.com"

        # Mock the get_user_by_id method to return the user
        with patch.object(service, 'get_user_by_id', return_value=mock_user):
            result = service.delete_user(1)

            # Verify the user was deleted from the session
            mock_db.delete.assert_called_once_with(mock_user)
            mock_db.commit.assert_called_once()

            assert result is True

    def test_delete_user_not_found(self):
        """Test attempting to delete a non-existent user."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock the get_user_by_id method to return None
        with patch.object(service, 'get_user_by_id', return_value=None):
            result = service.delete_user(999)

            # Verify nothing was deleted
            mock_db.delete.assert_not_called()
            mock_db.commit.assert_not_called()

            assert result is False


class TestUserServiceUserVerification:
    """Tests for user verification functionality."""

    def test_verify_user_email(self):
        """Test verifying user email."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock an existing user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "unverified@example.com"
        mock_user.is_verified = False

        # Mock the get_user_by_id method to return the user
        with patch.object(service, 'get_user_by_id', return_value=mock_user):
            result = service.verify_user_email(1)

            # Verify the user was marked as verified
            assert mock_user.is_verified is True

            # Verify the session was committed and refreshed
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_user)

            assert result == mock_user

    def test_verify_user_email_already_verified(self):
        """Test verifying an already verified user."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock an already verified user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "verified@example.com"
        mock_user.is_verified = True

        # Mock the get_user_by_id method to return the user
        with patch.object(service, 'get_user_by_id', return_value=mock_user):
            result = service.verify_user_email(1)

            # User should remain verified
            assert mock_user.is_verified is True

            # Verify the session was committed and refreshed
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_user)

            assert result == mock_user


class TestUserServiceUserStatus:
    """Tests for user status management."""

    def test_toggle_user_active_status(self):
        """Test toggling user active status."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock an existing user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "status@example.com"
        mock_user.is_active = True

        # Mock the get_user_by_id method to return the user
        with patch.object(service, 'get_user_by_id', return_value=mock_user):
            # First, deactivate the user
            deactivated_user = service.set_user_active_status(1, False)

            assert deactivated_user.is_active is False

            # Then reactivate the user
            reactivated_user = service.set_user_active_status(1, True)

            assert reactivated_user.is_active is True

    def test_lock_user_account(self):
        """Test locking user account after failed login attempts."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock an existing user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "locked@example.com"
        mock_user.failed_login_attempts = 3
        mock_user.is_active = True

        # Mock the get_user_by_id method to return the user
        with patch.object(service, 'get_user_by_id', return_value=mock_user):
            # Increment failed attempts to reach lockout threshold
            mock_user.failed_login_attempts = 5  # Assuming 5 is the threshold
            result = service.lock_user_account_if_needed(1, max_attempts=5)

            # User should be deactivated if attempts exceed threshold
            assert mock_user.is_active is False
            assert mock_user.failed_login_attempts == 5

    def test_reset_failed_login_attempts(self):
        """Test resetting failed login attempts after successful login."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock an existing user with failed attempts
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "reset@example.com"
        mock_user.failed_login_attempts = 3

        # Mock the get_user_by_id method to return the user
        with patch.object(service, 'get_user_by_id', return_value=mock_user):
            result = service.reset_failed_login_attempts(1)

            # Failed attempts should be reset to 0
            assert mock_user.failed_login_attempts == 0


class TestUserServiceUserQuerying:
    """Tests for user querying functionality."""

    def test_get_all_users(self):
        """Test retrieving all users."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock multiple users
        mock_users = [
            Mock(spec=User, id=1, email="user1@example.com", username="user1"),
            Mock(spec=User, id=2, email="user2@example.com", username="user2"),
            Mock(spec=User, id=3, email="user3@example.com", username="user3")
        ]

        # Mock the query result
        mock_query = Mock()
        mock_limit = Mock()

        mock_db.query.return_value = mock_query
        mock_query.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_users

        result = service.get_all_users(limit=10)

        # Verify the query was constructed correctly
        mock_db.query.assert_called_once_with(User)
        assert result == mock_users

    def test_get_users_paginated(self):
        """Test retrieving users with pagination."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock some users
        mock_users = [
            Mock(spec=User, id=i, email=f"user{i}@example.com", username=f"user{i}")
            for i in range(1, 6)
        ]

        # Mock the query result
        mock_query = Mock()
        mock_offset = Mock()
        mock_limit = Mock()

        mock_db.query.return_value = mock_query
        mock_query.offset.return_value = mock_offset
        mock_offset.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_users

        result = service.get_users_paginated(skip=0, limit=5)

        # Verify the query was constructed with offset and limit
        mock_db.query.assert_called_once_with(User)
        mock_query.offset.assert_called_once_with(0)
        mock_offset.limit.assert_called_once_with(5)
        assert result == mock_users

    def test_search_users(self):
        """Test searching for users by email or username."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock search results
        mock_users = [
            Mock(spec=User, id=1, email="search@example.com", username="searchuser")
        ]

        # Mock the query result
        mock_query = Mock()
        mock_filter = Mock()

        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.all.return_value = mock_users

        result = service.search_users("search")

        # Verify the query was constructed correctly
        mock_db.query.assert_called_once_with(User)
        assert result == mock_users


class TestUserServiceSecurity:
    """Tests for user security functionality."""

    def test_hash_password_method(self):
        """Test the hash_password utility method."""
        with patch('src.services.user_service.pwd_context') as mock_pwd_context:
            mock_pwd_context.hash.return_value = "hashed_test_password"

            result = UserService.hash_password("plaintext_password")

            assert result == "hashed_test_password"
            mock_pwd_context.hash.assert_called_once_with("plaintext_password")

    def test_increment_failed_login_attempts(self):
        """Test incrementing failed login attempts."""
        mock_db = Mock(spec=Session)
        service = UserService(mock_db)

        # Mock an existing user
        mock_user = Mock(spec=User)
        mock_user.id = 1
        mock_user.email = "failed@example.com"
        mock_user.failed_login_attempts = 2

        # Mock the get_user_by_id method to return the user
        with patch.object(service, 'get_user_by_id', return_value=mock_user):
            result = service.increment_failed_login_attempts(1)

            # Failed attempts should be incremented
            assert mock_user.failed_login_attempts == 3

            # Verify the session was committed and refreshed
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once_with(mock_user)

            assert result == mock_user