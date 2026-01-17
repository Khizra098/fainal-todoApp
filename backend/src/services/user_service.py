"""User service for the Todo Chatbot API."""
from sqlalchemy.orm import Session
from ..models.user import User

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