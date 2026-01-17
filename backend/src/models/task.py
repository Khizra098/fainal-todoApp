"""Database models for the Todo Chatbot application."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class TaskStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    in_progress = "in-progress"


class TaskPriority(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RoleType(enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class ConversationStatus(enum.Enum):
    active = "active"
    archived = "archived"
    completed = "completed"


class Task(Base):
    """Represents a single todo item with extended capabilities for AI interaction."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(500), nullable=False)  # max 500 chars
    status = Column(Enum(TaskStatus), default=TaskStatus.pending)  # enum: 'pending', 'completed', 'in-progress'
    created_date = Column(DateTime, default=datetime.utcnow)  # timestamp
    due_date = Column(DateTime, nullable=True)  # optional, nullable
    category = Column(String(100), nullable=True)  # optional, max 100 chars
    priority = Column(Enum(TaskPriority), default=TaskPriority.medium)  # enum: 'low', 'medium', 'high'
    user_id = Column(Integer, nullable=False)  # foreign key to user, for multi-user support

    def __repr__(self):
        return f"<Task(id={self.id}, description='{self.description}', status='{self.status}')>"


class Conversation(Base):
    """Maintains state for individual conversation threads with the AI agent."""

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)  # foreign key to user
    title = Column(String(200), nullable=False)  # auto-generated from first message, max 200 chars
    created_at = Column(DateTime, default=datetime.utcnow)  # timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # timestamp
    status = Column(Enum(ConversationStatus), default=ConversationStatus.active)  # enum: 'active', 'archived', 'completed'
    metadata_json = Column(JSON, nullable=True)  # additional conversation properties

    # Relationship to messages
    messages = relationship("Message", back_populates="conversation")

    def __repr__(self):
        return f"<Conversation(id={self.id}, user_id={self.user_id}, status='{self.status}')>"


class Message(Base):
    """Stores individual messages within a conversation."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)  # foreign key to conversation
    role = Column(Enum(RoleType), nullable=False)  # enum: 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)  # text content of the message
    timestamp = Column(DateTime, default=datetime.utcnow)  # timestamp
    metadata_json = Column(JSON, nullable=True)  # additional message properties like intent, entities

    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', conversation_id={self.conversation_id})>"


class IntentClassification(Base):
    """Maps natural language inputs to specific system actions."""

    __tablename__ = "intent_classifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)  # enum: 'CREATE_TODO', 'UPDATE_STATUS', 'SEARCH_TODOS', 'DELETE_TODO', 'LIST_TODOS', 'SET_REMINDER', 'OTHER'
    confidence = Column(Integer, nullable=False)  # 0 to 100 representing percentage
    entities_json = Column(JSON, nullable=True)  # extracted entities like dates, priorities, etc.

    def __repr__(self):
        return f"<IntentClassification(id={self.id}, name='{self.name}', confidence={self.confidence})>"