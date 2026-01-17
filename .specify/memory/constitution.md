<!-- Sync Impact Report:
Version change: 2.0.0 -> 3.0.0
Modified principles: Several principles updated for Phase 3 requirements
Added sections: New principles for AI chatbot, MCP tools, and stateless architecture
Removed sections: Web app specific principles now adapted for AI chatbot
Templates requiring updates: ✅ Updated
Follow-up TODOs: None
-->
# AI-Powered Todo Chatbot Constitution

## Core Principles

### Spec-Driven Development Only
All development must follow Spec-Driven Development methodology; No code shall be written without a corresponding specification; All logic must originate from specifications rather than ad-hoc implementation; Features must be defined in specs before implementation begins.

### No Manual Coding by Human
Human developers shall not manually write code; All code must be generated from specifications through automated processes; Direct code modifications without spec updates are prohibited; Code generation tools and AI assistance are required for all implementations.

### Stateless Backend Architecture
Application must follow stateless design principles; All application state must be externalized to databases or external services; Backend components must not maintain session state locally; Horizontal scaling must be supported without shared state between instances; Each request must be processed independently of others.

### MCP-Only Interaction for AI
AI agents must interact with the Todo application only via MCP (Model Context Protocol) tools; Direct database access or API calls from AI are prohibited; All data operations must flow through properly defined MCP tool interfaces; AI agents must use the same interfaces as human users; This ensures proper audit trails and security boundaries.

### Conversation State Persistence
Conversation context and history must be stored in the database; Each conversation thread must have its own persistent state; User interaction history must be maintained for continuity; Conversation metadata (timestamps, participants, status) must be tracked; Proper cleanup and retention policies must be implemented.

### OpenAI Agents SDK and Official MCP SDK Compliance
Application must use the OpenAI Agents SDK for AI agent functionality; Only the official MCP SDK must be used for context protocol implementation; Third-party alternatives to these SDKs are prohibited; Version compatibility must be maintained with official releases; Proper error handling for SDK operations is required.

### Persistent Storage with Neon PostgreSQL
Application must use Neon PostgreSQL for all data storage needs; No in-memory or temporary storage for user data; Data must persist across application restarts and deployments; All data operations must be performed on the PostgreSQL database; Proper connection pooling and error handling required.

## Additional Constraints

### Technology Stack
- Backend: Python with FastAPI for MCP tool endpoints
- AI: OpenAI Agents SDK with proper MCP integration
- Database: Neon PostgreSQL for conversation and task data
- MCP: Official MCP SDK for context protocol implementation
- Containerization: Docker for deployment consistency

### Performance Requirements
- AI response times under 5 seconds for most operations
- MCP tool calls under 1 second response time
- Efficient database queries with proper indexing
- Support for concurrent conversations without degradation
- AI token usage optimized for cost-effectiveness

### Security Standards
- All MCP tool calls must be properly authenticated
- Input validation required for all user inputs to AI
- Protection against prompt injection attacks
- Secure handling of sensitive data in conversations
- Proper access controls for conversation data
- AI privacy and data handling compliance

## Development Workflow

### Specification-First Process
- Every feature must begin with a detailed specification
- Specifications must include acceptance criteria
- Changes to specs require approval before implementation
- Test cases must be defined in specs before coding
- MCP tool contracts must be defined before implementation

### Quality Gates
- All code must pass linting and formatting checks
- Type safety required where applicable (Python type hints)
- Unit tests must cover 80%+ of business logic code
- Integration tests required for all MCP tools
- End-to-end tests required for AI conversation flows
- Code review required before merging

### Testing Requirements
- Test-driven development (TDD) approach encouraged for business logic
- Unit tests for all backend services and MCP tools
- Integration tests for AI agent interactions
- End-to-end tests for complete conversation scenarios
- Security tests for MCP tool access and data handling

## Governance

This constitution governs all development activities for the AI-Powered Todo Chatbot; All team members must comply with these principles; Amendments require formal approval and documentation; Deviations must be justified and tracked; Regular compliance reviews must occur during development cycles; Code generation tools must enforce these principles automatically where possible.

**Version**: 3.0.0 | **Ratified**: 2026-01-15 | **Last Amended**: 2026-01-15