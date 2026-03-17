"""Anki note type definitions used by AnkiConnect."""

from enum import StrEnum
from typing import Any


class NoteTypeName(StrEnum):
    """Anki note type names."""

    TARGET_TO_SOURCE = "AnkiAgent TargetToSource"
    SOURCE_TO_TARGET = "AnkiAgent SourceToTarget"
    GRAMMAR = "AnkiAgent Grammar"
    CLOZE = "AnkiAgent Cloze"


class ToolName(StrEnum):
    """Tool names for the Claude agent."""

    CREATE_VOCAB = "create_vocab_card"
    CREATE_GRAMMAR = "create_grammar_card"
    CREATE_CLOZE = "create_cloze_card"
    LIST_DECKS = "list_decks"


NOTE_TYPES: dict[NoteTypeName, dict[str, Any]] = {
    NoteTypeName.TARGET_TO_SOURCE: {
        "fields": ["Word", "IPA", "AnswerCount", "Translations", "Image"],
        "templates": [
            {
                "Name": "Card 1",
                "Front": "target_to_source_front.html",
                "Back": "target_to_source_back.html",
            }
        ],
    },
    NoteTypeName.SOURCE_TO_TARGET: {
        "fields": ["Word", "AnswerCount", "Translations", "Image"],
        "templates": [
            {
                "Name": "Card 1",
                "Front": "source_to_target_front.html",
                "Back": "source_to_target_back.html",
            }
        ],
    },
    NoteTypeName.GRAMMAR: {
        "fields": ["Rule", "Explanation", "Example", "IPA", "Image"],
        "templates": [
            {
                "Name": "Card 1",
                "Front": "grammar_front.html",
                "Back": "grammar_back.html",
            }
        ],
    },
    NoteTypeName.CLOZE: {
        "fields": ["Text", "Hint", "IPA", "Image"],
        "templates": [
            {
                "Name": "Card 1",
                "Front": "cloze_front.html",
                "Back": "cloze_back.html",
            }
        ],
    },
}
