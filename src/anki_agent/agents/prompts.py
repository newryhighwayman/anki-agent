"""System prompt and tool definitions for the Anki agent."""

from anki_agent.notes.note_defs import ToolName
from anki_agent.settings import Settings


def build_system_prompt(settings: Settings) -> str:
    """Build the system prompt using the user's language settings.

    Parameters
    ----------
    settings : Settings
        The user's settings.

    Returns
    -------
    str
        The system prompt for the Claude agent.
    """
    return f"""You are a language learning assistant that creates Anki flashcards. \
The user's source language is {settings.source_language} and they are \
learning {settings.target_language}.

The user can speak to you in any language. Translate as needed.

If a word has multiple meanings, ask the user which meaning(s) they \
want before creating the card.

Always confirm the card details before creating it.

You have the following tools available:
- create_vocab_card: Create vocabulary flashcards
- create_grammar_card: Create grammar flashcards
- create_cloze_card: Create cloze deletion flashcards
- list_decks: List available Anki decks"""


def build_tools(settings: Settings) -> list[dict]:
    """Build the tool definitions using the user's language settings.

    Parameters
    ----------
    settings : Settings
        The user's settings.

    Returns
    -------
    list of dict
        Tool definitions for the Claude API.
    """
    return [
        {
            "name": ToolName.CREATE_VOCAB,
            "description": (
                "Create vocabulary flashcards (target-to-source and "
                "source-to-target) with auto-fetched IPA, audio, "
                "and image."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "word": {
                        "type": "string",
                        "description": (f"The word in {settings.target_language}"),
                    },
                    "translations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "translation": {"type": "string"},
                                "example": {"type": "string"},
                            },
                            "required": ["translation"],
                        },
                        "description": ("List of translations with examples"),
                    },
                    "deck": {
                        "type": "string",
                        "description": "Anki deck name",
                        "default": settings.deck,
                    },
                    "image_description": {
                        "type": "string",
                        "description": ("DuckDuckGo search query for image"),
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags for the cards",
                    },
                },
                "required": ["word", "translations"],
            },
        },
        {
            "name": ToolName.CREATE_GRAMMAR,
            "description": "Create a grammar flashcard.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "rule": {"type": "string"},
                    "explanation": {"type": "string"},
                    "example": {"type": "string"},
                    "deck": {
                        "type": "string",
                        "default": settings.deck,
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["rule", "explanation", "example"],
            },
        },
        {
            "name": ToolName.CREATE_CLOZE,
            "description": "Create a cloze deletion flashcard.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": ("Text with {{c1::word}} syntax"),
                    },
                    "hint": {"type": "string"},
                    "deck": {
                        "type": "string",
                        "default": settings.deck,
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["text"],
            },
        },
        {
            "name": ToolName.LIST_DECKS,
            "description": "List all available Anki decks.",
            "input_schema": {
                "type": "object",
                "properties": {},
            },
        },
    ]
