"""
Unit tests for the message classifier service.
This module tests the message classification functionality.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.services.message_classifier import MessageClassifier


def test_classify_task_related_message():
    """Test that task-related messages are correctly classified"""
    classifier = MessageClassifier()

    task_related_messages = [
        "How do I add a new task?",
        "I want to complete my task",
        "Show me my tasks",
        "Delete this task",
        "Edit my task",
        "How do I create a task?",
        "I need to mark this as done",
        "What tasks do I have?",
        "Task management help",
        "How to manage tasks"
    ]

    for msg in task_related_messages:
        result = classifier.classify_message(msg)
        assert result == "task_related", f"Message '{msg}' should be classified as task_related"


def test_classify_greeting_message():
    """Test that greeting messages are correctly classified"""
    classifier = MessageClassifier()

    greeting_messages = [
        "Hello",
        "Hi",
        "Hey",
        "Good morning",
        "Good afternoon",
        "Good evening",
        "Greetings",
        "Howdy",
        "Hola",
        "Bonjour",
        "Hello there",
        "Hi there",
        "Hey there"
    ]

    for msg in greeting_messages:
        result = classifier.classify_message(msg)
        assert result == "greeting", f"Message '{msg}' should be classified as greeting"


def test_classify_non_task_message():
    """Test that non-task messages are correctly classified"""
    classifier = MessageClassifier()

    non_task_messages = [
        "What's the weather like?",
        "Tell me a joke",
        "How are you?",
        "What's your favorite color?",
        "I love pizza",
        "The sky is blue",
        "Random thought",
        "Nothing related to tasks",
        "This is off-topic",
        "Talk about sports",
        "Discuss movies",
        "Share a recipe"
    ]

    for msg in non_task_messages:
        result = classifier.classify_message(msg)
        assert result == "non_task", f"Message '{msg}' should be classified as non_task"


def test_classify_empty_message():
    """Test that empty messages are handled appropriately"""
    classifier = MessageClassifier()

    result = classifier.classify_message("")
    assert result in ["greeting", "non_task"], "Empty message should be classified as greeting or non_task"


def test_classify_mixed_keywords():
    """Test that messages with mixed keywords are classified based on dominant intent"""
    classifier = MessageClassifier()

    # Even with some task words, if the overall intent is greeting-like, it should be classified as greeting
    greeting_with_task_word = "Hi, can you help me with a task?"
    result = classifier.classify_message(greeting_with_task_word)
    assert result in ["greeting", "task_related"], f"Message '{greeting_with_task_word}' should be classified appropriately"


def test_classify_case_insensitive():
    """Test that classification is case insensitive"""
    classifier = MessageClassifier()

    original = "Hello"
    uppercase = "HELLO"
    lowercase = "hello"
    mixed_case = "HeLLo"

    original_result = classifier.classify_message(original)
    uppercase_result = classifier.classify_message(uppercase)
    lowercase_result = classifier.classify_message(lowercase)
    mixed_case_result = classifier.classify_message(mixed_case)

    assert original_result == uppercase_result == lowercase_result == mixed_case_result, \
        "Classification should be case insensitive"


def test_classify_with_punctuation():
    """Test that punctuation doesn't affect classification"""
    classifier = MessageClassifier()

    base_msg = "Hello"
    punctuated_msgs = [
        "Hello!",
        "Hello?",
        "Hello.",
        "Hello,",
        "Hello!!!",
        "Hello???"
    ]

    base_result = classifier.classify_message(base_msg)
    for msg in punctuated_msgs:
        result = classifier.classify_message(msg)
        assert result == base_result, f"Punctuation shouldn't affect classification: '{msg}' vs '{base_msg}'"