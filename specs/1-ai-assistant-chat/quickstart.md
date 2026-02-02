# Quickstart Guide: AI Assistant Chat

## Overview
This guide explains how to set up and use the AI Assistant Chat feature for the task management app.

## Prerequisites
- Python 3.11+
- Docker and Docker Compose
- Kubernetes cluster (Minikube for local development)
- OpenAI API key
- Neon PostgreSQL database

## Local Development Setup

### 1. Environment Configuration
```bash
# Copy the environment template
cp .env.example .env

# Update the environment variables in .env
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
MCP_SERVER_URL=http://localhost:8000
```

### 2. Database Setup
```bash
# Run database migrations
cd backend
python -m src.database.migrate

# Initialize conversation tables
python -m src.database.seed
```

### 3. Start Services
```bash
# Option 1: Using Docker Compose
docker-compose up --build

# Option 2: For development
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

### 4. Kubernetes Deployment (Local)
```bash
# Start Minikube
minikube start

# Deploy to local cluster
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/postgres-statefulset.yaml

# Port forward to access locally
kubectl port-forward service/backend 8000:80
```

## API Usage Examples

### Send a Message
```bash
curl -X POST http://localhost:8000/api/v1/chat/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
    "content": "How do I add a new task?",
    "message_type": "task_related"
  }'
```

### Create a New Conversation
```bash
curl -X POST http://localhost:8000/api/v1/conversations \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

## Testing

### Unit Tests
```bash
# Run all unit tests
cd backend
pytest tests/unit/

# Run specific test
pytest tests/unit/test_chat_service.py
```

### Integration Tests
```bash
# Run integration tests
cd backend
pytest tests/integration/
```

## MCP Tools Usage
The AI assistant communicates with the system through MCP tools:

```python
# Example of using the chat MCP tool
from mcp.chat_mcp import send_message_to_assistant

response = send_message_to_assistant(
    conversation_id="123e4567-e89b-12d3-a456-426614174000",
    user_message="How do I complete a task?",
    user_id="user-123"
)
```

## Troubleshooting

### Common Issues
1. **Database Connection**: Verify DATABASE_URL is correctly set
2. **API Rate Limits**: Check OpenAI API quota if responses are slow
3. **MCP Communication**: Ensure MCP server is running and accessible

### Logs
```bash
# View backend logs
kubectl logs -f deployment/backend

# View database logs
kubectl logs -f statefulset/postgres
```