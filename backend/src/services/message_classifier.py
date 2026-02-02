"""
Message classifier service for the AI Assistant Chat feature.
This module classifies messages into different types based on their content.
"""

import re
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class MessageClassifier:
    """
    Service class to classify messages into different categories:
    - task_related: Messages about task management
    - greeting: Greeting messages
    - non_task: Messages unrelated to tasks
    """

    def __init__(self):
        # Define keyword patterns for each category
        self.task_keywords = [
            "task", "add", "create", "delete", "remove", "complete", "finish", "done", "todo",
            "work", "project", "list", "item", "manage", "organize", "schedule", "deadline",
            "priority", "urgent", "important", "due", "assign", "share", "collaborate",
            "plan", "track", "monitor", "update", "edit", "modify", "change", "adjust"
        ]

        self.greeting_keywords = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "greetings", "howdy", "hola", "bonjour", "ciao", "namaste", "salutations",
            "morning", "afternoon", "evening", "day", "night", "welcome", "good day",
            "top of the morning", "g'day", "hallo", "guten tag", "nihao", "konichiwa",
            "annyeonghaseyo", "marhaban", "ahlan", "olá", "gracias", "buenos días",
            "buenas tardes", "buenas noches"
        ]

        # Compile regex patterns for more accurate matching
        self.task_pattern = re.compile(r'\b(?:' + '|'.join(self.task_keywords) + r')\b', re.IGNORECASE)
        self.greeting_pattern = re.compile(r'\b(?:' + '|'.join(self.greeting_keywords) + r')\b', re.IGNORECASE)

    def classify_message(self, message: str) -> str:
        """
        Classify a message into one of the predefined categories.

        Args:
            message (str): The message to classify

        Returns:
            str: The classification result ('task_related', 'greeting', or 'non_task')
        """
        if not message or not message.strip():
            # If message is empty or just whitespace, treat as greeting
            logger.debug("Empty message classified as greeting")
            return "greeting"

        message_lower = message.lower().strip()

        # Check for greetings first (they're often shorter and more direct)
        if self._contains_greeting_keywords(message_lower):
            logger.debug(f"Greeting message detected: '{message[:50]}...' -> greeting")
            return "greeting"

        # Check for task-related keywords
        if self._contains_task_keywords(message_lower):
            logger.debug(f"Task-related message detected: '{message[:50]}...' -> task_related")
            return "task_related"

        # If no specific keywords found, default to non-task
        logger.debug(f"No specific keywords found, defaulting to non_task: '{message[:50]}...' -> non_task")
        return "non_task"

    def _contains_greeting_keywords(self, message: str) -> bool:
        """
        Check if the message contains greeting keywords.

        Args:
            message (str): The message to check (lowercase)

        Returns:
            bool: True if greeting keywords are found, False otherwise
        """
        # Check for direct matches first
        for greeting in self.greeting_keywords:
            if greeting in message:
                return True

        # Use regex pattern for more robust matching
        return bool(self.greeting_pattern.search(message))

    def _contains_task_keywords(self, message: str) -> bool:
        """
        Check if the message contains task-related keywords.

        Args:
            message (str): The message to check (lowercase)

        Returns:
            bool: True if task keywords are found, False otherwise
        """
        # Check for direct matches first
        for task_keyword in self.task_keywords:
            if task_keyword in message:
                return True

        # Use regex pattern for more robust matching
        return bool(self.task_pattern.search(message))

    def get_confidence_scores(self, message: str) -> dict:
        """
        Get confidence scores for each classification category.

        Args:
            message (str): The message to analyze

        Returns:
            dict: Confidence scores for each category
        """
        if not message or not message.strip():
            return {"greeting": 0.8, "task_related": 0.1, "non_task": 0.1}

        message_lower = message.lower().strip()

        greeting_score = self._calculate_greeting_score(message_lower)
        task_score = self._calculate_task_score(message_lower)

        # Non-task score is based on the absence of other keywords
        non_task_score = max(0.1, 1.0 - (greeting_score + task_score))

        # Normalize scores so they sum to 1.0
        total = greeting_score + task_score + non_task_score
        if total > 0:
            greeting_score /= total
            task_score /= total
            non_task_score /= total

        return {
            "greeting": round(greeting_score, 2),
            "task_related": round(task_score, 2),
            "non_task": round(non_task_score, 2)
        }

    def _calculate_greeting_score(self, message: str) -> float:
        """
        Calculate a greeting confidence score based on keyword matches.

        Args:
            message (str): The message to analyze (lowercase)

        Returns:
            float: Greeting confidence score (0.0 to 1.0)
        """
        score = 0.0

        # Count direct matches
        for greeting in self.greeting_keywords:
            if greeting in message:
                score += 0.3  # Higher weight for greetings as they're typically clear-cut

        # Apply regex matching
        matches = self.greeting_pattern.findall(message)
        score += len(matches) * 0.2

        return min(score, 1.0)  # Cap at 1.0

    def _calculate_task_score(self, message: str) -> float:
        """
        Calculate a task-related confidence score based on keyword matches.

        Args:
            message (str): The message to analyze (lowercase)

        Returns:
            float: Task-related confidence score (0.0 to 1.0)
        """
        score = 0.0

        # Count direct matches
        for task_keyword in self.task_keywords:
            if task_keyword in message:
                score += 0.15  # Lower weight as task keywords might be used in broader contexts

        # Apply regex matching
        matches = self.task_pattern.findall(message)
        score += len(matches) * 0.1

        return min(score, 1.0)  # Cap at 1.0