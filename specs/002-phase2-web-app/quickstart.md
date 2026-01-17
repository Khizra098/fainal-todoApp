# Quickstart Guide: Phase 2 Todo Full-Stack Web Application

## Prerequisites

- Node.js v18+ (for frontend development)
- Python 3.9+ (for backend development)
- PostgreSQL-compatible database (Neon PostgreSQL)
- Docker and Docker Compose (recommended for deployment)
- Git

## Getting Started

### 1. Clone the Repository

```bash
git clone <repository-url>
cd todo-fullstack
```

### 2. Set Up Backend

#### Navigate to Backend Directory
```bash
cd backend
```

#### Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your database and authentication settings
```

#### Run Database Migrations
```bash
alembic upgrade head
```

#### Start Backend Server
```bash
uvicorn src.main:app --reload --port 8000
```

The backend server will be available at `http://localhost:8000`.

### 3. Set Up Frontend

#### Navigate to Frontend Directory
```bash
cd frontend
```

#### Install Dependencies
```bash
npm install
```

#### Set Up Environment Variables
```bash
cp .env.example .env
# Edit .env with your backend API URL
```

#### Start Frontend Server
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`.

### 4. Development Workflow

#### Backend Development
- API endpoints are defined in `src/api/routes/`
- Models are in `src/models/`
- Services are in `src/services/`
- Authentication is handled in `src/auth/`

#### Frontend Development
- Components are in `src/components/`
- Pages are in `src/pages/`
- API services are in `src/services/`
- Routes are configured in `src/App.jsx`

### 5. Running Tests

#### Backend Tests
```bash
cd backend
pytest
```

#### Frontend Tests
```bash
cd frontend
npm run test
```

### 6. Building for Production

#### Backend
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm run build
```

### 7. Using Docker (Recommended)

#### Build and Run Both Services
```bash
docker-compose up --build
```

#### Run in Background
```bash
docker-compose up -d
```

The application will be available at `http://localhost:3000` with the backend API at `http://localhost:8000`.

## API Documentation

The backend API documentation is automatically available at `http://localhost:8000/docs` when running in development mode.

## Authentication Flow

1. Register a new account at `/register`
2. Log in at `/login` to get a JWT token
3. Use the token in the Authorization header for protected endpoints
4. The frontend will handle token storage and inclusion in requests

## Database Setup

1. Ensure you have access to a PostgreSQL-compatible database (Neon)
2. Update the database URL in your `.env` file
3. Run migrations: `alembic upgrade head`

## Troubleshooting

- **Port already in use**: Change ports in `.env` files
- **Database connection errors**: Verify database URL and credentials
- **Authentication errors**: Ensure Better Auth is properly configured
- **Frontend/backend communication**: Check API URL in frontend environment variables