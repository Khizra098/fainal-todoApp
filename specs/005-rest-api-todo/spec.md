# Feature Specification: REST API for Phase 2 Todo App

**Feature Branch**: `005-rest-api-todo`
**Created**: 2026-01-15
**Status**: Draft
**Input**: User description: "Create REST API specification for Phase 2 Todo App. Include endpoints: GET /api/{user_id}/tasks, POST /api/{user_id}/tasks, GET /api/{user_id}/tasks/{id}, PUT /api/{user_id}/tasks/{id}, DELETE /api/{user_id}/tasks/{id}, PATCH /api/{user_id}/tasks/{id}/complete. Include: Request/response schemas, JWT requirement, Error responses"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - List User Tasks (Priority: P1)

As an authenticated user, I want to retrieve a list of my tasks so that I can see all my todo items.

**Why this priority**: This is fundamental functionality that allows users to view their tasks.

**Independent Test**: Can be fully tested by authenticating and making a GET request to retrieve the user's tasks, verifying the response contains the correct data.

**Acceptance Scenarios**:

1. **Given** I am authenticated with a valid JWT token, **When** I make a GET request to /api/{my_user_id}/tasks, **Then** I receive a 200 OK response with a list of my tasks
2. **Given** I am not authenticated, **When** I make a GET request to /api/{user_id}/tasks, **Then** I receive a 401 Unauthorized response

---

### User Story 2 - Create New Task (Priority: P1)

As an authenticated user, I want to create a new task so that I can add items to my todo list.

**Why this priority**: Essential for users to add new tasks to their personal list.

**Independent Test**: Can be fully tested by authenticating and making a POST request to create a new task, verifying it's properly stored and returned.

**Acceptance Scenarios**:

1. **Given** I am authenticated with a valid JWT token, **When** I make a POST request to /api/{my_user_id}/tasks with valid task data, **Then** I receive a 201 Created response with the new task details
2. **Given** I provide invalid task data, **When** I make a POST request, **Then** I receive a 400 Bad Request response with validation errors

---

### User Story 3 - Retrieve Specific Task (Priority: P2)

As an authenticated user, I want to retrieve a specific task so that I can view detailed information about it.

**Why this priority**: Important for users to access individual tasks when needed.

**Independent Test**: Can be fully tested by authenticating and making a GET request for a specific task, verifying the correct task is returned.

**Acceptance Scenarios**:

1. **Given** I am authenticated and own the task, **When** I make a GET request to /api/{my_user_id}/tasks/{task_id}, **Then** I receive a 200 OK response with the task details
2. **Given** I attempt to access a task that doesn't exist, **When** I make a GET request, **Then** I receive a 404 Not Found response

---

### User Story 4 - Update Task Details (Priority: P2)

As an authenticated user, I want to update my task details so that I can modify task information.

**Why this priority**: Critical for task management - users need to update task details like title, description, etc.

**Independent Test**: Can be fully tested by authenticating and making a PUT request to update a task, verifying the changes are saved.

**Acceptance Scenarios**:

1. **Given** I am authenticated and own the task, **When** I make a PUT request to /api/{my_user_id}/tasks/{task_id} with updated data, **Then** I receive a 200 OK response with the updated task
2. **Given** I attempt to update someone else's task, **When** I make a PUT request, **Then** I receive a 403 Forbidden response

---

### User Story 5 - Delete Task (Priority: P2)

As an authenticated user, I want to delete my task so that I can remove items I no longer need.

**Why this priority**: Important for task list maintenance and management.

**Independent Test**: Can be fully tested by authenticating and making a DELETE request to remove a task, verifying it's properly deleted.

**Acceptance Scenarios**:

1. **Given** I am authenticated and own the task, **When** I make a DELETE request to /api/{my_user_id}/tasks/{task_id}, **Then** I receive a 204 No Content response and the task is removed
2. **Given** I attempt to delete someone else's task, **When** I make a DELETE request, **Then** I receive a 403 Forbidden response

---

### User Story 6 - Complete Task (Priority: P2)

As an authenticated user, I want to mark my task as complete so that I can track my progress.

**Why this priority**: Important for task lifecycle management - users need to mark tasks as completed.

**Independent Test**: Can be fully tested by authenticating and making a PATCH request to complete a task, verifying the status is updated.

**Acceptance Scenarios**:

1. **Given** I am authenticated and own the task, **When** I make a PATCH request to /api/{my_user_id}/tasks/{task_id}/complete, **Then** I receive a 200 OK response and the task status is updated to completed
2. **Given** I attempt to complete someone else's task, **When** I make a PATCH request, **Then** I receive a 403 Forbidden response

---

### Edge Cases

- What happens when a user attempts to access another user's tasks?
- How does the system handle expired JWT tokens?
- What occurs when malformed JSON is sent in the request body?
- How does the system behave when required fields are missing from requests?
- What happens when the same request is made multiple times (idempotency)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST require valid JWT token in Authorization header for all endpoints
- **FR-002**: System MUST only allow users to access tasks associated with their own user ID
- **FR-003**: GET /api/{user_id}/tasks MUST return a list of tasks for the specified user
- **FR-004**: POST /api/{user_id}/tasks MUST create a new task for the specified user
- **FR-005**: GET /api/{user_id}/tasks/{id} MUST return details of the specified task
- **FR-006**: PUT /api/{user_id}/tasks/{id} MUST update the entire task with the provided data
- **FR-007**: DELETE /api/{user_id}/tasks/{id} MUST permanently remove the specified task
- **FR-008**: PATCH /api/{user_id}/tasks/{id}/complete MUST update only the task's completion status
- **FR-009**: System MUST return appropriate HTTP status codes for all operations
- **FR-010**: System MUST return detailed error messages in standardized format

### Request/Response Schemas

#### Task Object Schema
```
{
  "id": integer,
  "user_id": integer,
  "title": string,
  "description": string,
  "status": "pending" | "completed",
  "created_at": string (ISO 8601),
  "updated_at": string (ISO 8601)
}
```

#### GET /api/{user_id}/tasks
- **Method**: GET
- **Headers**: Authorization: Bearer {jwt_token}
- **Response 200**: Array<TaskObject>
- **Response 401**: Unauthorized error object
- **Response 403**: Forbidden error object
- **Response 404**: Not found error object

#### POST /api/{user_id}/tasks
- **Method**: POST
- **Headers**: Authorization: Bearer {jwt_token}, Content-Type: application/json
- **Request Body**:
```
{
  "title": string (required, min 1 character),
  "description": string (optional, max 500 characters),
}
```
- **Response 201**: TaskObject
- **Response 400**: Validation error object
- **Response 401**: Unauthorized error object
- **Response 403**: Forbidden error object

#### GET /api/{user_id}/tasks/{id}
- **Method**: GET
- **Headers**: Authorization: Bearer {jwt_token}
- **Response 200**: TaskObject
- **Response 401**: Unauthorized error object
- **Response 403**: Forbidden error object
- **Response 404**: Not found error object

#### PUT /api/{user_id}/tasks/{id}
- **Method**: PUT
- **Headers**: Authorization: Bearer {jwt_token}, Content-Type: application/json
- **Request Body**:
```
{
  "title": string (required, min 1 character),
  "description": string (optional, max 500 characters),
  "status": "pending" | "completed"
}
```
- **Response 200**: TaskObject
- **Response 400**: Validation error object
- **Response 401**: Unauthorized error object
- **Response 403**: Forbidden error object
- **Response 404**: Not found error object

#### DELETE /api/{user_id}/tasks/{id}
- **Method**: DELETE
- **Headers**: Authorization: Bearer {jwt_token}
- **Response 204**: No content
- **Response 401**: Unauthorized error object
- **Response 403**: Forbidden error object
- **Response 404**: Not found error object

#### PATCH /api/{user_id}/tasks/{id}/complete
- **Method**: PATCH
- **Headers**: Authorization: Bearer {jwt_token}, Content-Type: application/json
- **Request Body**:
```
{
  "status": "completed"
}
```
- **Response 200**: TaskObject
- **Response 400**: Validation error object
- **Response 401**: Unauthorized error object
- **Response 403**: Forbidden error object
- **Response 404**: Not found error object

#### Error Response Schema
```
{
  "error": {
    "code": string,
    "message": string,
    "details": array (optional)
  }
}
```

### Key Entities *(include if feature involves data)*

- **Task**: Represents a todo item with attributes ID, UserID, Title, Description, Status, CreatedAt, UpdatedAt
- **User**: Represents an authenticated user with attributes ID, associated tasks
- **APIRequest**: Represents an incoming API request with attributes Endpoint, Method, Headers, Body, AuthToken
- **APIResponse**: Represents an outgoing API response with attributes StatusCode, Body, Headers

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 99% of authenticated API requests return appropriate responses under normal load
- **SC-002**: API responds to requests within 500ms for 95% of requests under normal load
- **SC-003**: Users can only access their own tasks (0% unauthorized cross-user access incidents)
- **SC-004**: 95% of validation errors return appropriate error messages to clients
- **SC-005**: JWT tokens are properly validated for all protected endpoints