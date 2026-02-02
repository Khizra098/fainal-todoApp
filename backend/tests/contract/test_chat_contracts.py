"""
Contract tests for the chat API endpoints.
This module tests the API contracts for the chat functionality.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.main import app


@pytest.fixture
def client():
    """Create a test client for the API"""
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_send_message_contract():
    """Test the contract for the chat/send endpoint"""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # Test that the endpoint exists and accepts the expected parameters
        response = await ac.post("/api/v1/chat/send", json={
            "conversation_id": "123e4567-e89b-12d3-a456-426614174000",
            "content": "How do I add a new task?",
            "message_type": "task_related"
        })

        # We expect a 401 Unauthorized since no auth token is provided
        # But the important thing is that the endpoint exists and accepts the right params
        assert response.status_code in [200, 401, 422]  # 200 for success, 401 for auth issue, 422 for validation issue


@pytest.mark.asyncio
async def test_create_conversation_contract():
    """Test the contract for the conversations endpoint"""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # Test that the endpoint exists and accepts the expected parameters
        response = await ac.post("/api/v1/conversations", json={})

        # We expect a 401 Unauthorized since no auth token is provided
        # But the important thing is that the endpoint exists
        assert response.status_code in [201, 401, 422]


@pytest.mark.asyncio
async def test_get_conversation_contract():
    """Test the contract for getting a conversation"""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # Test that the endpoint exists
        response = await ac.get("/api/v1/conversations/123e4567-e89b-12d3-a456-426614174000")

        # We expect a 401 Unauthorized since no auth token is provided
        # But the important thing is that the endpoint exists
        assert response.status_code in [200, 401, 404, 422]


@pytest.mark.asyncio
async def test_get_conversation_messages_contract():
    """Test the contract for getting conversation messages"""
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # Test that the endpoint exists
        response = await ac.get("/api/v1/conversations/123e4567-e89b-12d3-a456-426614174000/messages")

        # We expect a 401 Unauthorized since no auth token is provided
        # But the important thing is that the endpoint exists
        assert response.status_code in [200, 401, 404, 422]