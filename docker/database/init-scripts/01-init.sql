-- PostgreSQL initialization script
-- Create tables and initial data for the todo application

-- Create todos table
CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_todos_completed ON todos(completed);
CREATE INDEX IF NOT EXISTS idx_todos_created_at ON todos(created_at);

-- Insert sample data
INSERT INTO todos (title, description, completed) VALUES
    ('Sample Todo 1', 'This is a sample todo item', FALSE),
    ('Sample Todo 2', 'Another sample todo item', TRUE)
ON CONFLICT DO NOTHING;

-- Create a dedicated application user if it doesn't exist
DO $$
BEGIN
    CREATE USER app_user WITH PASSWORD 'app_password';
EXCEPTION
    WHEN duplicate_object THEN
        RAISE NOTICE 'User already exists';
END
$$;

-- Grant privileges to the application user
GRANT CONNECT ON DATABASE todo_app TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO app_user;