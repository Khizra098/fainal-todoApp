# ADR: Todo AI Chatbot Architecture

## Status
Proposed

## Context
The Todo AI Chatbot requires several key architectural decisions to align with the project constitution while enabling natural language interaction with the todo system. The system must follow stateless architecture, use MCP-only interactions for AI agents, and leverage official SDKs as mandated by the constitution.

## Decision

### 1. MCP-Only Interaction Pattern
AI agents will interact with the todo system exclusively through MCP (Model Context Protocol) tools. This ensures proper audit trails, security boundaries, and compliance with the constitution's requirement that "AI agents must interact with the Todo application only via MCP tools".

### 2. Stateless Backend with External Persistence
The backend follows a stateless design where all application state is externalized to Neon PostgreSQL. This supports horizontal scaling and ensures no shared state between instances as required by the constitution.

### 3. Technology Stack
- Backend: FastAPI with Python 3.11 for robust API capabilities and async support
- AI Integration: OpenAI Agents SDK with official MCP SDK
- Database: Neon PostgreSQL for persistent storage
- Frontend: React with ChatKit for the chat interface
- Communication: REST APIs and MCP protocols

### 4. Separation of Concerns
Clear separation between backend (API and MCP tools) and frontend (chat interface) to enable independent scaling and maintenance.

## Consequences

### Positive
- Ensures compliance with project constitution
- Enables proper security and auditability through MCP-only interactions
- Supports horizontal scaling through stateless architecture
- Leverages official SDKs for stability and support
- Clear separation allows for independent development

### Negative
- Increased complexity compared to direct integration
- Potential latency overhead from MCP tool calls
- Need for additional infrastructure components

## Alternatives Considered

### Direct Database Access
Rejected because it violates the constitution's MCP-only requirement and lacks proper security boundaries.

### Monolithic Architecture
Rejected because it doesn't support the required separation of AI interactions and doesn't scale as well as the proposed approach.

## Notes
This architecture balances the constitutional requirements with practical implementation needs while supporting the core functionality of natural language todo management.