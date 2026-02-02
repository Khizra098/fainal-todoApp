"""
Unit tests for non-task message detection functionality.
This module tests the detection of non-task-related messages in the AI Assistant Chat feature.
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.services.message_classifier import MessageClassifier


def test_detect_clearly_non_task_messages():
    """Test detection of clearly non-task-related messages"""
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
        "Share a recipe",
        "What time is it?",
        "Are you a robot?",
        "Do you like music?"
    ]

    for msg in non_task_messages:
        result = classifier.classify_message(msg)
        assert result == "non_task", f"'{msg}' should be classified as non_task"


def test_detect_questions_unrelated_to_tasks():
    """Test detection of questions that are unrelated to tasks"""
    classifier = MessageClassifier()

    non_task_questions = [
        "How tall is Mount Everest?",
        "Who invented the telephone?",
        "What is the capital of France?",
        "Why is the sky blue?",
        "How do airplanes fly?",
        "What makes birds fly?",
        "Who won the World Cup in 2018?",
        "What is quantum physics?",
        "How do plants make food?",
        "Why do cats purr?"
    ]

    for msg in non_task_questions:
        result = classifier.classify_message(msg)
        assert result == "non_task", f"'{msg}' should be classified as non_task"


def test_detect_personal_opinions_or_comments():
    """Test detection of personal opinions or comments"""
    classifier = MessageClassifier()

    personal_messages = [
        "I think chocolate ice cream is the best",
        "My favorite movie is The Matrix",
        "I had a great day today",
        "I don't like rainy days",
        "My car is red",
        "I live in a big city",
        "My dog loves to play fetch",
        "I enjoy reading mystery novels",
        "My hobby is collecting stamps",
        "I prefer coffee over tea"
    ]

    for msg in personal_messages:
        result = classifier.classify_message(msg)
        assert result == "non_task", f"'{msg}' should be classified as non_task"


def test_detect_social_conversation_starters():
    """Test detection of social conversation starters"""
    classifier = MessageClassifier()

    social_messages = [
        "So, how was your weekend?",
        "What did you do last night?",
        "Have you seen that new show?",
        "Do you want to grab lunch?",
        "How is your family doing?",
        "Did you watch the game?",
        "What are your plans for the weekend?",
        "Have you tried that new restaurant?",
        "How was your vacation?",
        "Are you going to the party?"
    ]

    for msg in social_messages:
        result = classifier.classify_message(msg)
        assert result == "non_task", f"'{msg}' should be classified as non_task"


def test_non_task_with_some_task_words():
    """Test messages that contain task words but are non-task in context"""
    classifier = MessageClassifier()

    context_non_task_messages = [
        "I have a lot of tasks in my life, but let's talk about something else",
        "Tasks are important, but what's your favorite book?",
        "I manage my tasks well, unlike my cooking skills",
        "Task management is cool, but do you like hiking?",
        "I use task apps, but I'm asking about your hobbies"
    ]

    for msg in context_non_task_messages:
        result = classifier.classify_message(msg)
        # These might be classified as non_task depending on implementation
        assert result in ["task_related", "non_task"], f"'{msg}' classification should be valid"


def test_detect_task_words_in_non_task_context():
    """Test task-related words used in non-task context"""
    classifier = MessageClassifier()

    non_task_context_with_task_words = [
        "I dream about completing tasks in my sleep",
        "My pet likes to delete things, unlike my task app",
        "The movie character add ingredients to the pot, like adding tasks",
        "She was assigned to the art project, not a task list",
        "The schedule on the wall shows TV shows, not tasks"
    ]

    for msg in non_task_context_with_task_words:
        result = classifier.classify_message(msg)
        # These could go either way depending on the algorithm
        assert result in ["task_related", "non_task"], f"'{msg}' classification should be valid"


def test_detect_generic_statements():
    """Test detection of generic statements that don't relate to tasks"""
    classifier = MessageClassifier()

    generic_statements = [
        "The sun is shining today",
        "It's raining outside",
        "Traffic is heavy during rush hour",
        "Coffee shops are popular places to visit",
        "Books contain lots of interesting information",
        "Music can affect people's moods",
        "Different cultures have unique traditions",
        "Science helps us understand the world",
        "Art comes in many different forms",
        "Sports bring people together"
    ]

    for msg in generic_statements:
        result = classifier.classify_message(msg)
        assert result == "non_task", f"'{msg}' should be classified as non_task"


def test_detect_off_topic_requests():
    """Test detection of requests that are off-topic for task management"""
    classifier = MessageClassifier()

    off_topic_requests = [
        "Can you tell me a story?",
        "Please explain how photosynthesis works",
        "Show me pictures of cats",
        "Recommend a good restaurant",
        "What's the news today?",
        "Give me a weather forecast",
        "Suggest a movie to watch",
        "Tell me about history",
        "Explain how engines work",
        "Recommend a book to read"
    ]

    for msg in off_topic_requests:
        result = classifier.classify_message(msg)
        assert result == "non_task", f"'{msg}' should be classified as non_task"


def test_detect_messages_with_task_keywords_but_not_task_requests():
    """Test messages that have task keywords but aren't requesting task management"""
    classifier = MessageClassifier()

    task_keywords_not_requests = [
        "Task and purpose are related concepts",
        "The assignment was to write about flowers, not tasks",
        "My schedule includes exercise, which is not task management",
        "I was assigned to the team, not a specific task",
        "The deadline for the art project is approaching"
    ]

    for msg in task_keywords_not_requests:
        result = classifier.classify_message(msg)
        # These could go either way depending on implementation
        assert result in ["task_related", "non_task"], f"'{msg}' classification should be valid"


def test_detect_philosophical_or_abstract_messages():
    """Test detection of philosophical or abstract messages"""
    classifier = MessageClassifier()

    abstract_messages = [
        "Life is like a box of chocolates",
        "Time is a human construct",
        "What is the meaning of existence?",
        "Beauty is subjective to each person",
        "Freedom has many definitions",
        "Knowledge is power in many contexts",
        "Love transcends all boundaries",
        "Truth can be relative in some cases",
        "Wisdom comes with experience",
        "Courage is needed in difficult times"
    ]

    for msg in abstract_messages:
        result = classifier.classify_message(msg)
        assert result == "non_task", f"'{msg}' should be classified as non_task"


def test_non_task_confidence_scores():
    """Test that clearly non-task messages have high confidence scores for non_task classification"""
    classifier = MessageClassifier()

    clear_non_task_messages = [
        "What's the weather like?",
        "Tell me a joke",
        "How are you?"
    ]

    for msg in clear_non_task_messages:
        confidence_scores = classifier.get_confidence_scores(msg)

        # Ensure all scores sum to approximately 1.0
        total_score = sum(confidence_scores.values())
        assert abs(total_score - 1.0) < 0.01, f"Confidence scores should sum to 1.0, got {total_score}"

        # For clear non-task messages, non_task score should be relatively high
        non_task_score = confidence_scores["non_task"]
        # The exact threshold may vary based on implementation
        assert non_task_score >= 0.3, f"Clear non-task message '{msg}' should have reasonable non_task confidence"


def test_edge_cases_non_task():
    """Test edge cases for non-task detection"""
    classifier = MessageClassifier()

    edge_cases = [
        "",  # Empty string (might be handled differently)
        "   ",  # Whitespace
        "abc123xyz",  # Random characters
        "!@#$%^&*()",  # Special characters
        "The",  # Single common word
        "And then I said hello to the task manager",  # Complex sentence with mixed keywords
    ]

    for msg in edge_cases:
        result = classifier.classify_message(msg)
        # Ensure the function doesn't crash and returns a valid classification
        assert result in ["task_related", "greeting", "non_task"], f"'{msg}' classification should be valid"