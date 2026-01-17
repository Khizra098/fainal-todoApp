# Data Model: Phase 2 Todo Full-Stack Web Application

## Entity Definitions

### User Entity
Represents a registered user in the system with authentication details.

**Attributes**:
- `id`: SERIAL PRIMARY KEY - Auto-incrementing unique identifier
- `email`: VARCHAR(255) UNIQUE NOT NULL - User's email address
- `password_hash`: VARCHAR(255) NOT NULL - Securely hashed password
- `created_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP - Account creation timestamp
- `updated_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP - Last update timestamp
- `is_active`: BOOLEAN NOT NULL DEFAULT TRUE - Account status flag
- `last_login_at`: TIMESTAMP - Timestamp of last successful login

**Validation Rules**:
- Email must be a valid email format
- Password hash must not be empty
- Email must be unique across all users
- Created and updated timestamps are automatically managed

**State Transitions**:
- Active ↔ Inactive (based on account status)

### Task Entity
Represents a todo item associated with a specific user.

**Attributes**:
- `id`: SERIAL PRIMARY KEY - Auto-incrementing unique identifier
- `user_id`: INTEGER NOT NULL - Foreign key reference to users table
- `title`: VARCHAR(255) NOT NULL - Task title/summary
- `description`: TEXT - Detailed task description (optional)
- `status`: VARCHAR(20) NOT NULL DEFAULT 'pending' - Task status ('pending', 'completed')
- `created_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP - Task creation timestamp
- `updated_at`: TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP - Last update timestamp

**Validation Rules**:
- Title must not be empty
- Status must be either 'pending' or 'completed'
- User_id must reference a valid user
- Created and updated timestamps are automatically managed

**State Transitions**:
- Pending → Completed (when task is finished)
- Completed → Pending (when task is unmarked)

## Relationships

### User to Tasks (One-to-Many)
- **Type**: One user can have many tasks
- **Constraint**: Foreign Key: tasks.user_id references users.id
- **Behavior**: Cascade Delete - When a user is deleted, all their tasks are automatically deleted
- **Access Pattern**: A user can only access their own tasks

### Data Integrity Constraints

**Primary Keys**:
- Ensure unique identification of records in both users and tasks tables

**Foreign Keys**:
- Maintain referential integrity between users and tasks
- Prevent orphaned tasks without valid users

**Unique Constraints**:
- Prevent duplicate email addresses in the users table

**Check Constraints**:
- Validate status values ('pending', 'completed')
- Ensure title is not empty
- Validate email format

**Not Null Constraints**:
- Ensure required fields are present

**Default Values**:
- Provide sensible defaults for optional fields (status='pending', is_active=TRUE)

## Indexing Strategy

### Users Table
- `idx_users_email`: ON email (for authentication lookups)
- `idx_users_active`: ON is_active (for filtering active accounts)

### Tasks Table
- `idx_tasks_user_id`: ON user_id (for user-specific queries)
- `idx_tasks_user_status`: ON user_id, status (for filtered user queries)
- `idx_tasks_created_at`: ON created_at (for chronological ordering)

## Business Rules

1. **User Isolation**: Each user can only access their own tasks
2. **Data Consistency**: All timestamps are in UTC
3. **Soft Deletes**: Consider implementing soft deletes for data recovery
4. **Audit Trail**: Track important changes for accountability
5. **Validation**: All data must pass validation before being stored

## API Mapping

The data model maps to API endpoints as follows:
- User entity relates to authentication endpoints
- Task entity relates to all task management endpoints
- Relationships ensure proper authorization checks