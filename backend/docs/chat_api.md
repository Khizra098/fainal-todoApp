# AI Assistant Chat API Documentation

## Overview
The AI Assistant Chat API provides intelligent chat capabilities focused on task management. The API handles three primary message types:
- Task-related queries (with polite, helpful guidance)
- Greetings (with warm, brief responses)
- Non-task messages (with boundary-setting responses)

## Authentication
All API endpoints require authentication using JWT tokens. Include an Authorization header with the format: `Bearer <token>`.

## Endpoints

### POST /api/v1/chat/send
Send a message to the AI assistant and receive a response.

#### Request Body
```json
{
  "conversation_id": "string (UUID)",
  "content": "string (message content, max 10000 chars)",
  "message_type": "string (optional hint: task_related, greeting, non_task)"
}
```

#### Response
```json
{
  "conversation_id": "string",
  "response": "string (AI assistant's response)",
  "success": "boolean"
}
```

### GET /api/v1/chat/analysis
Analyze a message to get its classification and confidence scores.

#### Query Parameters
- `message`: The message to analyze (required)

#### Response
```json
{
  "analysis": {
    "classification": "string (task_related, greeting, non_task)",
    "confidence_scores": {
      "greeting": "float",
      "task_related": "float",
      "non_task": "float"
    },
    "timestamp": "string (ISO format)"
  },
  "success": "boolean"
}
```

### POST /api/v1/conversations
Create a new conversation.

#### Request Body
```json
{
  "initial_message": "string (optional first message)"
}
```

#### Response
```json
{
  "conversation_id": "string (UUID)",
  "created_at": "string (ISO format)",
  "updated_at": "string (ISO format)",
  "status": "string (active, archived, suspended)",
  "user_id": "string",
  "success": "boolean"
}
```

### GET /api/v1/conversations/{conversation_id}
Get details of a specific conversation.

#### Response
```json
{
  "conversation_id": "string (UUID)",
  "created_at": "string (ISO format)",
  "updated_at": "string (ISO format)",
  "status": "string (active, archived, suspended)",
  "user_id": "string",
  "success": "boolean"
}
```

### GET /api/v1/conversations/{conversation_id}/messages
Get messages for a specific conversation.

#### Query Parameters
- `limit`: Maximum number of messages (default: 50, max: 100)
- `offset`: Number of messages to skip (default: 0)

#### Response
```json
{
  "messages": [
    {
      "message_id": "string (UUID)",
      "conversation_id": "string (UUID)",
      "sender_type": "string (user, ai_assistant)",
      "content": "string",
      "timestamp": "string (ISO format)",
      "message_type": "string"
    }
  ],
  "total_count": "integer",
  "limit": "integer",
  "offset": "integer",
  "success": "boolean"
}
```

### GET /api/v1/conversations
Get all conversations for the current user.

#### Query Parameters
- `limit`: Maximum number of conversations (default: 20, max: 100)
- `offset`: Number of conversations to skip (default: 0)

#### Response
```json
{
  "conversations": [
    {
      "conversation_id": "string (UUID)",
      "created_at": "string (ISO format)",
      "updated_at": "string (ISO format)",
      "status": "string (active, archived, suspended)",
      "user_id": "string",
      "metadata": "string (JSON)"
    }
  ],
  "limit": "integer",
  "offset": "integer",
  "success": "boolean"
}
```

## Message Classification
The system automatically classifies incoming messages into three categories:

### Task-Related Messages
Messages that ask about or refer to task management, including:
- Adding, creating, or making tasks
- Completing, finishing, or marking tasks
- Deleting, removing, or canceling tasks
- Organizing or managing tasks
- Questions about task status or progress

### Greeting Messages
Friendly salutations including:
- "Hello", "Hi", "Hey"
- "Good morning/afternoon/evening"
- "Greetings", "Howdy", "Welcome"
- Cultural greetings like "Hola", "Bonjour", etc.

### Non-Task Messages
Messages unrelated to task management that trigger boundary-setting responses.

## Response Types
The system generates different types of responses based on the message classification:
- Task Guidance: Helpful instructions for task management
- Greeting: Warm, brief welcome messages
- Boundary Setting: Directs users back to task-related queries

## Error Handling
The API returns appropriate HTTP status codes:
- 200: Successful requests
- 400: Bad request (invalid parameters)
- 401: Unauthorized (authentication required)
- 403: Forbidden (insufficient permissions)
- 404: Not found (resource doesn't exist)
- 500: Internal server error

## Rate Limiting
API endpoints may be subject to rate limiting to ensure fair usage across all users.