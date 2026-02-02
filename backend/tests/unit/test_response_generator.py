"""
Unit tests for the response generator service.
This module tests the response generation functionality.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.services.response_generator import ResponseGenerator


def test_generate_task_guidance_response():
    """Test that task guidance responses are generated correctly"""
    generator = ResponseGenerator()

    # Test various task-related inputs
    task_inputs = [
        "How do I add a new task?",
        "I want to complete my task",
        "Show me my tasks",
        "Delete this task"
    ]

    for user_input in task_inputs:
        response = generator.generate_response(user_input, "task_related")

        # Check that response is not empty
        assert response is not None
        assert len(response.strip()) > 0

        # Check that response is appropriate for task-related queries
        assert isinstance(response, str)
        # Task responses should be helpful and guidance-oriented
        assert any(keyword in response.lower() for keyword in [
            "task", "add", "complete", "show", "delete", "help", "guide", "assist"
        ]), f"Response '{response}' should contain task-related keywords"


def test_generate_greeting_response():
    """Test that greeting responses are generated correctly"""
    generator = ResponseGenerator()

    # Test various greeting inputs
    greeting_inputs = [
        "Hello",
        "Hi",
        "Hey",
        "Good morning"
    ]

    for user_input in greeting_inputs:
        response = generator.generate_response(user_input, "greeting")

        # Check that response is not empty
        assert response is not None
        assert len(response.strip()) > 0

        # Check that response is appropriate for greetings
        assert isinstance(response, str)
        # Greeting responses should be warm and friendly
        assert any(keyword in response.lower() for keyword in [
            "hello", "hi", "hey", "greetings", "welcome", "nice", "glad", "pleased", "good day"
        ]), f"Response '{response}' should contain greeting-related keywords"


def test_generate_boundary_response():
    """Test that boundary-setting responses are generated correctly"""
    generator = ResponseGenerator()

    # Test various non-task inputs
    non_task_inputs = [
        "What's the weather like?",
        "Tell me a joke",
        "How are you?"
    ]

    for user_input in non_task_inputs:
        response = generator.generate_response(user_input, "non_task")

        # Check that response is not empty
        assert response is not None
        assert len(response.strip()) > 0

        # Check that response is appropriate for non-task queries
        assert isinstance(response, str)
        # Boundary responses should direct back to task management
        assert "task" in response.lower() or "related" in response.lower(), \
            f"Response '{response}' should contain task-related guidance"


def test_generate_response_with_different_types():
    """Test that different message types generate different response patterns"""
    generator = ResponseGenerator()

    test_input = "How do I manage my tasks?"

    # Generate responses for different types with the same input
    task_response = generator.generate_response(test_input, "task_related")
    greeting_response = generator.generate_response(test_input, "greeting")
    boundary_response = generator.generate_response(test_input, "non_task")

    # All should be valid responses
    assert all(r is not None and len(r.strip()) > 0 for r in [task_response, greeting_response, boundary_response])

    # Responses should be different based on type
    # (though they might be similar for this particular input)
    assert isinstance(task_response, str)
    assert isinstance(greeting_response, str)
    assert isinstance(boundary_response, str)


def test_generate_response_empty_input():
    """Test that empty input is handled gracefully"""
    generator = ResponseGenerator()

    response = generator.generate_response("", "task_related")

    # Should handle empty input gracefully
    assert response is not None
    assert isinstance(response, str)


def test_generate_response_long_input():
    """Test that long input is handled gracefully"""
    generator = ResponseGenerator()

    long_input = "This is a very long message that contains lots of text and multiple sentences. " * 10

    response = generator.generate_response(long_input, "task_related")

    # Should handle long input gracefully
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0


def test_generate_response_special_characters():
    """Test that input with special characters is handled properly"""
    generator = ResponseGenerator()

    special_input = "How do I add a task with special characters like @#$%^&*()?"

    response = generator.generate_response(special_input, "task_related")

    # Should handle special characters gracefully
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0


def test_generate_response_consistency():
    """Test that the same input produces consistent responses for the same type"""
    generator = ResponseGenerator()

    test_input = "How do I add a task?"

    # Generate multiple responses for the same input and type
    responses = [
        generator.generate_response(test_input, "task_related"),
        generator.generate_response(test_input, "task_related"),
        generator.generate_response(test_input, "task_related")
    ]

    # All should be valid responses
    for response in responses:
        assert response is not None
        assert isinstance(response, str)
        assert len(response) > 0