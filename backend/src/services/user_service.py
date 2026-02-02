"""User service for the Todo Chatbot API."""
from sqlalchemy.orm import Session
from ..models.user import User
import pyotp


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, name: str, email: str, password_hash: str) -> User:
        """Create a new user."""
        user = User(
            name=name,
            email=email,
            password_hash=password_hash
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_email(self, email: str) -> User:
        """Get a user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> User:
        """Get a user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def update_user(self, user_id: int, **kwargs) -> User:
        """Update user information."""
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):  # Only set attributes that exist on the user model
                    setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        user = self.get_user_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False

    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password after verifying current password."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        # Import the password verification function from auth_handler for bcrypt consistency
        from ..auth.auth_handler import verify_password, get_password_hash

        # Verify current password (using bcrypt)
        if not verify_password(current_password, user.password_hash):
            return False

        # Hash and update new password using bcrypt
        new_password_hash = get_password_hash(new_password)
        user.password_hash = new_password_hash
        self.db.commit()
        return True

    def toggle_two_factor(self, user_id: int, enable: bool) -> bool:
        """Toggle two-factor authentication for user."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.two_factor_enabled = enable
        if not enable:
            user.two_factor_secret = None
        self.db.commit()
        return True

    def setup_two_factor(self, user_id: int) -> tuple[str, str]:
        """Setup two-factor authentication for user."""
        user = self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        # Generate a random secret
        secret = pyotp.random_base32()
        user.two_factor_secret = secret
        self.db.commit()

        # Generate QR code for authenticator apps
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name="Todo Chatbot"
        )

        return secret, totp_uri

    def verify_two_factor_code(self, user_id: int, code: str) -> bool:
        """Verify two-factor authentication code."""
        user = self.get_user_by_id(user_id)
        if not user or not user.two_factor_secret:
            return False

        totp = pyotp.TOTP(user.two_factor_secret)
        return totp.verify(code)