# Implementation Plan: Phase 2 Todo Full-Stack Web Application

## Technical Context

**Project Name**: Todo Full-Stack Web Application
**Phase**: 2
**Architecture**: Monorepo with separate frontend and backend components
**Authentication**: Better Auth with JWT-based authentication
**Database**: Neon PostgreSQL for persistent storage
**Frontend**: Modern web framework for responsive UI
**Backend**: FastAPI (Python) for REST API endpoints
**Deployment**: Containerized application with separate services

**Unknowns (NEEDS CLARIFICATION)**:
- Specific frontend framework choice (React, Vue, Angular)
- Exact Neon PostgreSQL setup and connection details
- Better Auth integration specifics with FastAPI
- Deployment infrastructure details

## Constitution Check

This implementation plan adheres to the Todo Full-Stack Web Application Constitution:

- ✅ **Spec-Driven Development Only**: Following specifications from specs/overview.md, task-crud spec, authentication spec, API spec, database spec, and UI spec
- ✅ **No Manual Coding by Human**: Using code generation tools and AI assistance
- ✅ **Clean Architecture Structure**: Separating frontend and backend with clear boundaries
- ✅ **Monorepo Structure**: Organizing as a monorepo with distinct frontend and backend components
- ✅ **JWT-Based Authentication**: Implementing Better Auth with JWT tokens
- ✅ **User Data Isolation**: Ensuring each user can only access their own tasks
- ✅ **Persistent Storage with Neon PostgreSQL**: Using Neon PostgreSQL for data persistence

## Gates Evaluation

- ✅ **Technology Alignment**: Selected technologies align with constitution requirements
- ✅ **Architecture Compliance**: Proposed architecture follows clean separation of concerns
- ✅ **Security Standards**: Plan includes proper authentication and authorization
- ✅ **Scalability Considerations**: Architecture supports concurrent users

## Phase 0: Outline & Research

### Research Tasks

**Task 0.1**: Research frontend framework options for the todo application
- **Decision**: Use React with TypeScript for the frontend
- **Rationale**: React has excellent ecosystem, strong community support, and good integration with authentication libraries
- **Alternatives considered**: Vue.js, Angular, vanilla JavaScript frameworks

**Task 0.2**: Research Better Auth integration with FastAPI
- **Decision**: Use Better Auth with JWT middleware for FastAPI
- **Rationale**: Better Auth provides easy integration and handles JWT generation/validation automatically
- **Alternatives considered**: Auth0, Firebase Auth, custom JWT implementation

**Task 0.3**: Research Neon PostgreSQL setup and connection pooling
- **Decision**: Use psycopg2-binary with connection pooling for database connections
- **Rationale**: Neon PostgreSQL is PostgreSQL-compatible, so standard PostgreSQL drivers work
- **Alternatives considered**: SQLAlchemy, async drivers like asyncpg

**Task 0.4**: Research monorepo tooling options
- **Decision**: Use a simple folder structure with separate package.json and requirements.txt files
- **Rationale**: For this project size, complex monorepo tools like Nx or Lerna add unnecessary overhead
- **Alternatives considered**: Nx, Lerna, Rush, simple folder structure

## Phase 1: Design & Contracts

### Data Model

Based on the database schema specification:

**Users Table**:
- id (SERIAL PRIMARY KEY): Auto-incrementing unique identifier
- email (VARCHAR(255) UNIQUE NOT NULL): User's email address
- password_hash (VARCHAR(255) NOT NULL): Securely hashed password
- created_at (TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP): Account creation timestamp
- updated_at (TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP): Last update timestamp
- is_active (BOOLEAN NOT NULL DEFAULT TRUE): Account status flag
- last_login_at (TIMESTAMP): Timestamp of last successful login

**Tasks Table**:
- id (SERIAL PRIMARY KEY): Auto-incrementing unique identifier
- user_id (INTEGER NOT NULL): Foreign key reference to users table
- title (VARCHAR(255) NOT NULL): Task title/summary
- description (TEXT): Detailed task description (optional)
- status (VARCHAR(20) NOT NULL DEFAULT 'pending'): Task status ('pending', 'completed')
- created_at (TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP): Task creation timestamp
- updated_at (TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP): Last update timestamp

**Relationships**:
- One-to-Many: One user can have many tasks
- Foreign Key Constraint: tasks.user_id references users.id
- Cascade Delete: When a user is deleted, all their tasks are automatically deleted

### API Contracts

Based on the REST API specification:

**Endpoints**:
- GET /api/{user_id}/tasks - Retrieve all tasks for a user
- POST /api/{user_id}/tasks - Create a new task for a user
- GET /api/{user_id}/tasks/{id} - Retrieve a specific task
- PUT /api/{user_id}/tasks/{id} - Update an entire task
- DELETE /api/{user_id}/tasks/{id} - Delete a specific task
- PATCH /api/{user_id}/tasks/{id}/complete - Update task completion status

**Authentication**:
- All endpoints require valid JWT token in Authorization header
- Users can only access their own resources (user_id must match authenticated user)

### Monorepo Structure

```
todo-fullstack/
├── backend/
│   ├── src/
│   │   ├── main.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── task.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── task_service.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       └── tasks.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   └── jwt_handler.py
│   │   └── database/
│   │       ├── __init__.py
│   │       └── database.py
│   ├── requirements.txt
│   ├── alembic/
│   │   └── versions/
│   ├── alembic.ini
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_auth.py
│       └── test_tasks.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── TaskList.jsx
│   │   │   └── TaskForm.jsx
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   └── DashboardPage.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── auth.js
│   │   ├── utils/
│   │   │   └── constants.js
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   ├── vite.config.js
│   └── tests/
│       └── App.test.jsx
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── .gitignore
├── README.md
└── .env.example
```

## Phase 2: Implementation Strategy

### Backend Plan

**Tech Stack**:
- FastAPI: Modern Python web framework with automatic API documentation
- SQLAlchemy: ORM for database operations
- Better Auth: Authentication provider
- Neon PostgreSQL: Cloud-native PostgreSQL
- PyJWT: JWT token handling
- Uvicorn: ASGI server

**Implementation Steps**:
1. Set up project structure with requirements.txt
2. Configure database connection with Neon PostgreSQL
3. Implement user model and authentication endpoints
4. Create task model and CRUD operations
5. Implement JWT-based authentication middleware
6. Create API routes for all required endpoints
7. Add validation and error handling
8. Write unit and integration tests

### Frontend Plan

**Tech Stack**:
- React: Component-based UI library
- TypeScript: Type safety
- Vite: Build tool
- Axios: HTTP client
- React Router: Client-side routing
- Tailwind CSS: Styling framework

**Implementation Steps**:
1. Set up React project with TypeScript and Vite
2. Create component structure based on UI spec
3. Implement authentication pages (Login, Register)
4. Create dashboard with task list UI
5. Implement task management functionality (Add/Edit/Delete)
6. Add responsive design for different screen sizes
7. Connect to backend API endpoints
8. Add form validation and error handling
9. Write unit tests for components

### Auth Integration Steps

1. **Better Auth Setup**:
   - Configure Better Auth with email/password authentication
   - Set up JWT token generation and validation
   - Configure session management

2. **Backend Integration**:
   - Create JWT middleware to protect routes
   - Implement user verification in API endpoints
   - Ensure user isolation (users can only access their own data)

3. **Frontend Integration**:
   - Implement login/logout functionality
   - Store JWT tokens securely (preferably in memory, not localStorage for production)
   - Add authentication headers to API requests
   - Redirect unauthenticated users to login page

4. **Testing**:
   - Test authentication flow end-to-end
   - Verify user data isolation
   - Test token expiration and refresh