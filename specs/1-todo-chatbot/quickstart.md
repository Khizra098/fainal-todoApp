# Quickstart Guide: Todo AI Chatbot

## Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or Neon PostgreSQL account)
- OpenAI API key
- MCP SDK

## Setup Instructions

### Backend Setup
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd todo-chatbot/backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key and database credentials
   ```

4. Set up the database:
   ```bash
   python -m src.database.setup
   ```

5. Run the backend server:
   ```bash
   uvicorn src.main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd todo-chatbot/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your backend API URL
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

## Usage

### Starting the Chat Interface
1. Visit `http://localhost:3000` in your browser
2. You'll see the chat interface with a message input box
3. Start chatting with the AI assistant using natural language

### Example Interactions
- "Add buy groceries to my todo list"
- "Show me my pending tasks"
- "Mark task #1 as completed"
- "Set a reminder for my meeting tomorrow at 2pm"

## Development

### Running Tests
Backend tests:
```bash
pytest tests/unit/
pytest tests/integration/
```

Frontend tests:
```bash
npm run test
```

### Adding New MCP Tools
1. Define the new tool in `src/services/mcp_tool_service.py`
2. Add the schema to the contracts
3. Register the tool with the AI agent
4. Test the new functionality

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: Connection string for PostgreSQL database
- `MCP_SERVER_URL`: URL for MCP server (if separate)
- `DEBUG`: Enable/disable debug mode