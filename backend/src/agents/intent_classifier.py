"""Intent classifier for natural language processing in the Todo Chatbot."""
import re
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class IntentType(Enum):
    CREATE_TODO = "CREATE_TODO"
    UPDATE_STATUS = "UPDATE_STATUS"
    SEARCH_TODOS = "SEARCH_TODOS"
    DELETE_TODO = "DELETE_TODO"
    LIST_TODOS = "LIST_TODOS"
    SET_REMINDER = "SET_REMINDER"
    OTHER = "OTHER"


@dataclass
class IntentResult:
    intent: IntentType
    confidence: float
    entities: Dict[str, any]


class IntentClassifier:
    """
    Classifies natural language inputs into specific system actions.
    """

    def __init__(self):
        """Initialize the intent classifier with patterns and keywords."""
        # Patterns for different intents
        self.patterns = {
            IntentType.CREATE_TODO: [
                r'\b(add|create|make|new)\b.*\b(todo|task|item|thing|do|to-do)\b',
                r'\b(create|add)\b.*\b(list|task|todo)\b',
                r'\b(put|add|write|note)\b.*\b(down|on|my)\b.*\b(list|todo|task)\b',
                r'\b(need to|want to|should|must)\b.*\b(do|finish|complete|buy|get|call|send|write)\b',
            ],
            IntentType.UPDATE_STATUS: [
                r'\b(complete|done|finished|mark as done|check off)\b',
                r'\b(mark|set)\b.*\b(done|completed|as completed)\b',
                r'\b(finish|complete|tick off)\b.*\b(task|todo|item)\b',
            ],
            IntentType.SEARCH_TODOS: [
                r'\b(find|search|look for|show me|where is|locate)\b',
                r'\b(search|find)\b.*\b(my|the)\b.*\b(todos|tasks|list)\b',
            ],
            IntentType.DELETE_TODO: [
                r'\b(delete|remove|erase|clear|get rid of)\b.*\b(todo|task|item)\b',
                r'\b(remove|delete)\b.*\b(from|off)\b.*\b(list|my list)\b',
            ],
            IntentType.LIST_TODOS: [
                r'\b(show|display|list|tell me|what are|what\'s on)\b.*\b(my|the)\b.*\b(todos|tasks|list)\b',
                r'\b(what|list|show)\b.*\b(i have|to do|on my list)\b',
                r'\b(my|the)\b.*\b(todos|tasks|list|things to do)\b',
            ],
            IntentType.SET_REMINDER: [
                r'\b(remind|set reminder|remind me|alarm|notify me)\b',
                r'\b(reminder|alert|notification)\b.*\b(set|create|make)\b',
            ]
        }

        # Keywords for entities extraction
        self.priority_keywords = {
            'high': ['urgent', 'important', 'asap', 'high', 'critical', 'priority'],
            'medium': ['normal', 'medium', 'regular'],
            'low': ['low', 'not urgent', 'later', 'whenever']
        }

        self.status_keywords = {
            'completed': ['completed', 'done', 'finished', 'marked'],
            'pending': ['pending', 'not done', 'incomplete', 'to do'],
            'in-progress': ['in progress', 'working on', 'started']
        }

    def classify_intent(self, text: str) -> IntentResult:
        """
        Classify the intent of a natural language input.

        Args:
            text: The natural language input to classify

        Returns:
            IntentResult with the classified intent, confidence score, and extracted entities
        """
        text_lower = text.lower().strip()
        scores = {}

        # Score each intent based on pattern matches
        for intent, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1
            scores[intent] = score

        # Find the intent with the highest score
        best_intent = max(scores.keys(), key=lambda x: scores[x])
        max_score = scores[best_intent]

        # Calculate confidence (simple heuristic based on number of matches)
        total_matches = sum(scores.values())
        confidence = min(max_score / max(total_matches, 1), 1.0) if total_matches > 0 else 0.0

        # Ensure a minimum confidence threshold
        if confidence < 0.1:
            best_intent = IntentType.OTHER
            confidence = 0.0

        # Extract entities
        entities = self.extract_entities(text_lower)

        return IntentResult(
            intent=best_intent,
            confidence=confidence,
            entities=entities
        )

    def extract_entities(self, text: str) -> Dict[str, any]:
        """
        Extract entities like dates, priorities, and task descriptions from the text.

        Args:
            text: The text to extract entities from

        Returns:
            Dictionary of extracted entities
        """
        entities = {}

        # Extract priority
        for priority, keywords in self.priority_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    entities['priority'] = priority
                    break
            if 'priority' in entities:
                break

        # Extract status
        for status, keywords in self.status_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    entities['status'] = status
                    break
            if 'status' in entities:
                break

        # Extract dates (basic implementation)
        date_patterns = [
            r'tomorrow',
            r'next week',
            r'next month',
            r'next year',
            r'today',
            r'in \d+ days?',
            r'in \d+ weeks?',
            r'in \d+ months?',
            r'on \w+ \d{1,2}(?:st|nd|rd|th)?',
            r'by \w+ \d{1,2}(?:st|nd|rd|th)?',
            r'before \w+ \d{1,2}(?:st|nd|rd|th)?',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                entities['date'] = match.group()
                break

        # Extract task ID if mentioned
        id_match = re.search(r'(?:task|item|number|id)\s*(?:#|is\s*)?(\d+)', text, re.IGNORECASE)
        if id_match:
            entities['task_id'] = int(id_match.group(1))

        # Extract search query if it contains search keywords
        search_match = re.search(r'(?:find|search|look for|show me)\s+(.+?)(?:\s+in|\s+on|\s+from|$)', text, re.IGNORECASE)
        if search_match:
            entities['search_query'] = search_match.group(1).strip()

        return entities


# Example usage
if __name__ == "__main__":
    classifier = IntentClassifier()

    test_inputs = [
        "Add buy groceries to my todo list for tomorrow",
        "Mark finish report as completed",
        "Show me my pending tasks",
        "Set a reminder for my dentist appointment next week",
        "Delete task #3 from my list"
    ]

    for test_input in test_inputs:
        result = classifier.classify_intent(test_input)
        print(f"Input: {test_input}")
        print(f"Intent: {result.intent.value}, Confidence: {result.confidence:.2f}")
        print(f"Entities: {result.entities}")
        print("---")