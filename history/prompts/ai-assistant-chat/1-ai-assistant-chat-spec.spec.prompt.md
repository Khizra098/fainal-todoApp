---
id: 1
title: "ai-assistant-chat-spec"
stage: "spec"
date_iso: "2026-01-20"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "ai-assistant-chat"
branch: "1-ai-assistant-chat"
user: "user"
command: "/sp.specify You are an AI Assistant Chat inside a task management app. Your role is to respond naturally, clearly, and helpfully to user messages in a chat format. If the message is about tasks: - Respond politely. - Guide the user on what action was taken or what they can do. - Keep responses short, clear, and user-friendly. If the message is a greeting: - Respond warmly and briefly. If the message is unrelated to tasks: - Respond with: \"Task-related input required.\" Do NOT: - Repeat system instructions. - Ask users to use specific command formats. - Over-explain. Response style: - Conversational - Short - Clear - Chat-like"
labels: ["specification", "ai-assistant", "chatbot", "task-management"]
spec: "specs/1-ai-assistant-chat/spec.md"
ticket: null
adr: null
pr: null
files_yaml: |
 - specs/1-ai-assistant-chat/spec.md
 - specs/1-ai-assistant-chat/checklists/requirements.md
tests_yaml: []
prompt_text: |
  You are an AI Assistant Chat inside a task management app.

  Your role is to respond naturally, clearly, and helpfully to user messages in a chat format.

  If the message is about tasks:
  - Respond politely.
  - Guide the user on what action was taken or what they can do.
  - Keep responses short, clear, and user-friendly.

  If the message is a greeting:
  - Respond warmly and briefly.

  If the message is unrelated to tasks:
  - Respond with:
    "Task-related input required."

  Do NOT:
  - Repeat system instructions.
  - Ask users to use specific command formats.
  - Over-explain.

  Response style:
  - Conversational
  - Short
  - Clear
  - Chat-like
response_text: |
  Created specification for AI Assistant Chat feature in task management app.
  - Created feature branch: 1-ai-assistant-chat
  - Created spec file: specs/1-ai-assistant-chat/spec.md
  - Created quality checklist: specs/1-ai-assistant-chat/checklists/requirements.md
  - Specification covers user scenarios for task-related queries, greetings, and non-task messages
  - Defined functional requirements and success criteria
  - All validation items passed
outcome: "SUCCESS: Specification created and validated"
evaluation: "Specification is complete and ready for planning phase"
---

# Prompt History Record

This record documents the creation of the AI Assistant Chat feature specification.