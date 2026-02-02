# Data Model: AI Assistant Chat for Task Management App

## Entities

### Conversation
Represents a single conversation thread between a user and the AI assistant.

- **conversation_id**: UUID (Primary Key) - Unique identifier for the conversation
- **created_at**: DateTime - Timestamp when conversation started
- **updated_at**: DateTime - Timestamp of last activity
- **user_id**: UUID (Foreign Key) - Reference to the user who initiated the conversation
- **status**: String (active, archived, suspended) - Current state of the conversation
- **metadata**: JSON - Additional conversation properties

### Message
Represents a single message in a conversation, either from the user or the AI assistant.

- **message_id**: UUID (Primary Key) - Unique identifier for the message
- **conversation_id**: UUID (Foreign Key) - Reference to the parent conversation
- **sender_type**: String (user, ai_assistant) - Indicates the sender of the message
- **content**: Text - The actual message content
- **timestamp**: DateTime - When the message was sent
- **message_type**: String (task_related, greeting, non_task, response) - Classification of the message
- **sentiment_score**: Float - Sentiment analysis score (-1.0 to 1.0)

### Response
Represents the AI assistant's response to a user message, including the processing details.

- **response_id**: UUID (Primary Key) - Unique identifier for the response
- **message_id**: UUID (Foreign Key) - Reference to the user message being responded to
- **content**: Text - The AI assistant's response content
- **generated_at**: DateTime - When the response was generated
- **response_type**: String (task_guidance, greeting, boundary_setting) - Type of response provided
- **processing_time_ms**: Integer - Time taken to generate the response
- **confidence_score**: Float - Confidence in the appropriateness of the response (0.0 to 1.0)

## Relationships

- Conversation (1) ←→ Messages (Many): A conversation contains multiple messages
- Message (1) ←→ Response (0 or 1): A user message may have an associated AI response

## Validation Rules

### Conversation
- created_at must be before updated_at
- status must be one of the allowed values
- user_id must reference a valid user

### Message
- content must not be empty
- sender_type must be either 'user' or 'ai_assistant'
- message_type must be one of: 'task_related', 'greeting', 'non_task', 'response'
- timestamp must be reasonable (not in the future)

### Response
- content must not be empty
- response_type must be one of: 'task_guidance', 'greeting', 'boundary_setting'
- confidence_score must be between 0.0 and 1.0

## State Transitions

### Conversation Status
- active → archived (when conversation is completed)
- active → suspended (when conversation violates terms)
- suspended → active (when reinstated by admin)