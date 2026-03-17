from __future__ import annotations

import json
import logging

import anthropic

from anki_agent.agents.prompts import build_system_prompt, build_tools
from anki_agent.audio import get_audio_provider
from anki_agent.client import AnkiClient
from anki_agent.config import ANTHROPIC_MODEL
from anki_agent.notes.builder import NoteBuilder
from anki_agent.notes.duplicates import check_vocab_duplicate
from anki_agent.notes.note_defs import NoteTypeName, ToolName
from anki_agent.notes.templates import ensure_models_exist
from anki_agent.settings import load_settings

logger = logging.getLogger(__name__)


class AnkiAgent:
    """Claude-powered conversational agent for creating Anki cards."""

    def __init__(
        self,
        anki_client: AnkiClient | None = None,
        _anthropic_client: anthropic.Anthropic | None = None,
    ) -> None:
        self._anthropic = _anthropic_client or anthropic.Anthropic()
        self._anki = anki_client or AnkiClient()
        self._settings = load_settings()
        self._audio_provider = get_audio_provider(
            self._settings.audio_provider,
            language_code=self._settings.target_language_code,
            **self._settings.audio_options,
        )
        self._system_prompt = build_system_prompt(self._settings)
        self._tools = build_tools(self._settings)
        self._messages: list[dict] = []
        self._models_ensured = False

    def _ensure_models(self) -> None:
        """Create custom Anki models on first tool use."""
        if not self._models_ensured:
            ensure_models_exist(self._anki)
            self._models_ensured = True

    def chat(self, message: str) -> str:
        """Send a message and get the agent's response.

        Parameters
        ----------
        message : str
            The user's message.

        Returns
        -------
        str
            The agent's text response.
        """
        self._messages.append({"role": "user", "content": message})

        while True:
            response = self._anthropic.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=4096,
                system=self._system_prompt,
                tools=self._tools,
                messages=self._messages,
            )

            self._messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self._handle_tool(block.name, block.input)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(result),
                            }
                        )
                self._messages.append({"role": "user", "content": tool_results})
            else:
                break

        text_parts = []
        for block in response.content:
            if hasattr(block, "text"):
                text_parts.append(block.text)

        return "\n".join(text_parts)

    def _handle_tool(self, name: ToolName, inputs: dict) -> dict:
        """Dispatch a tool call to the appropriate handler method."""
        self._ensure_models()

        match name:
            case ToolName.CREATE_VOCAB:
                result = self._create_vocab(inputs)
            case ToolName.CREATE_GRAMMAR:
                result = self._create_grammar(inputs)
            case ToolName.CREATE_CLOZE:
                result = self._create_cloze(inputs)
            case ToolName.LIST_DECKS:
                result = {"decks": self._anki.deck_names()}
            case _:
                result = {"error": f"Unknown tool: {name}"}

        return result

    def _create_vocab(self, inputs: dict) -> dict:
        """Build and add vocabulary cards from tool inputs."""
        deck = inputs.get("deck", self._settings.deck)
        tags = inputs.get("tags", [])
        image = inputs.get("image_description", True)
        word = inputs["word"]

        warnings = []
        translations_to_add = []

        for t in inputs["translations"]:
            translation = t["translation"]
            dup = check_vocab_duplicate(
                self._anki,
                word,
                NoteTypeName.TARGET_TO_SOURCE,
                translation,
            )

            if dup.status == "duplicate":
                warnings.append(
                    f"'{word}' already has translation '{translation}' — skipped."
                )
            elif dup.status == "updatable":
                new_translations = f"{dup.existing_translations}<br>{translation}"
                if t.get("example"):
                    new_translations = (
                        f"{dup.existing_translations}<br>{translation} — {t['example']}"
                    )
                self._anki.update_note_fields(
                    dup.existing_note_id,
                    {"Translations": new_translations},
                )
                warnings.append(
                    f"Updated existing card for '{word}' with "
                    f"new translation '{translation}'."
                )
            else:
                translations_to_add.append(t)

        if not translations_to_add:
            return {
                "success": True,
                "cards_created": 0,
                "warnings": warnings,
            }

        builder = NoteBuilder(
            deck=deck,
            tags=tags,
            audio_provider=self._audio_provider,
        )
        for t in translations_to_add:
            builder.add_vocab(
                target_word=word,
                source_word=t["translation"],
                example=t.get("example", ""),
                image=image,
            )

        notes = builder.build()
        ids = self._anki.add_notes(notes)

        result = {
            "success": True,
            "cards_created": len(ids),
            "note_ids": ids,
        }
        if warnings:
            result["warnings"] = warnings

        return result

    def _create_grammar(self, inputs: dict) -> dict:
        """Build and add a grammar card from tool inputs."""
        deck = inputs.get("deck", self._settings.deck)
        tags = inputs.get("tags", [])

        builder = NoteBuilder(
            deck=deck,
            tags=tags,
            audio_provider=self._audio_provider,
        )
        builder.add_grammar(
            rule=inputs["rule"],
            explanation=inputs["explanation"],
            example=inputs["example"],
        )

        notes = builder.build()
        ids = self._anki.add_notes(notes)

        return {
            "success": True,
            "cards_created": len(ids),
            "note_ids": ids,
        }

    def _create_cloze(self, inputs: dict) -> dict:
        """Build and add a cloze deletion card from tool inputs."""
        deck = inputs.get("deck", self._settings.deck)
        tags = inputs.get("tags", [])

        builder = NoteBuilder(
            deck=deck,
            tags=tags,
            audio_provider=self._audio_provider,
        )
        builder.add_cloze(
            text=inputs["text"],
            hint=inputs.get("hint", ""),
        )

        notes = builder.build()
        ids = self._anki.add_notes(notes)

        return {
            "success": True,
            "cards_created": len(ids),
            "note_ids": ids,
        }
