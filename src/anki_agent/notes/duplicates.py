from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from anki_agent.client import AnkiClient


@dataclass
class DuplicateResult:
    """Result of checking whether a vocab card already exists."""

    status: Literal["new", "duplicate", "updatable"]
    existing_note_id: int | None = None
    existing_translations: str = ""


def check_vocab_duplicate(
    client: AnkiClient,
    word: str,
    model_name: str,
    translation: str,
) -> DuplicateResult:
    """Check if a vocab note already exists for the given word and model.

    Parameters
    ----------
    client : AnkiClient
        The Anki client to query.

    word : str
        The word to search for.

    model_name : str
        The Anki model name (e.g. `"AnkiAgent TargetToSource"`).

    translation : str
        The translation to check against existing translations.

    Returns
    -------
    DuplicateResult
        The duplicate status with existing note details if found.
    """
    query = f'"Word:{word}" "note:{model_name}"'
    note_ids = client.find_notes(query)

    if not note_ids:
        result = DuplicateResult(status="new")
    else:
        notes_info = client.get_notes_info(note_ids)
        note = notes_info[0]
        existing = note["fields"]["Translations"]["value"]

        if translation in existing:
            result = DuplicateResult(
                status="duplicate",
                existing_note_id=note["noteId"],
                existing_translations=existing,
            )
        else:
            result = DuplicateResult(
                status="updatable",
                existing_note_id=note["noteId"],
                existing_translations=existing,
            )

    return result
