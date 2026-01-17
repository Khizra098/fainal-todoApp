# Data Models: Todo AI Chatbot

## Core Entities

### Task Model
Represents a single todo item with extended capabilities for AI interaction.

```python
class Task:
    id: int (primary key, auto-increment)
    description: str (max 500 chars)
    status: str (enum: 'pending', 'completed', 'in-progress')
    created_date: datetime (timestamp)
    due_date: datetime (optional, nullable)
    category: str (optional, max 100 chars)
    priority: str (enum: 'low', 'medium', 'high', default: 'medium')
    user_id: int (foreign key to user, for multi-user support)
```

### Conversation Model
Maintains state for individual conversation threads with the AI agent.

```python
class Conversation:
    id: int (primary key, auto-increment)
    user_id: int (foreign key to user)
    title: str (auto-generated from first message, max 200 chars)
    created_at: datetime (timestamp)
    updated_at: datetime (timestamp)
    status: str (enum: 'active', 'archived', 'completed')
    metadata: jsonb (additional conversation properties)
```

### Message Model
Stores individual messages within a conversation.

```python
class Message:
    id: int (primary key, auto-increment)
    conversation_id: int (foreign key to conversation)
    role: str (enum: 'user', 'assistant', 'system')
    content: str (text content of the message)
    timestamp: datetime (timestamp)
    metadata: jsonb (additional message properties like intent, entities)
```

### IntentClassification Model
Maps natural language inputs to specific system actions.

```python
class IntentClassification:
    id: int (primary key, auto-increment)
    name: str (enum: 'CREATE_TODO', 'UPDATE_STATUS', 'SEARCH_TODOS', 'DELETE_TODO', 'LIST_TODOS', 'SET_REMINDER', 'OTHER')
    confidence: float (0.0 to 1.0)
    entities: jsonb (extracted entities like dates, priorities, etc.)
```

### MCPTool Model
Defines which MCP tools to invoke for specific advanced functionalities.

```python
class MCPTool:
    id: int (primary key, auto-increment)
    name: str (unique name of the tool)
    description: str (what the tool does)
    parameters: jsonb (expected parameters)
    response_schema: jsonb (expected response format)
```

## Relationships

- One User has many Conversations
- One Conversation has many Messages
- One Conversation has many IntentClassifications (through messages)
- One Message has one IntentClassification (optional)

## Indexes

- Task: indexes on user_id, status, due_date for efficient querying
- Conversation: indexes on user_id, created_at, status
- Message: indexes on conversation_id, timestamp
- Task: partial index on (user_id, status) WHERE status = 'pending' for common query

## Constraints

- Task description must not be empty
- Due date must be in the future if provided
- Status must be one of allowed values
- Priority must be one of allowed values
- Conversation status transitions follow specific rules
- Message role must be one of allowed values