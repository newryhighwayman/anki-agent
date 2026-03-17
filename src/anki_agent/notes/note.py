from dataclasses import dataclass, field
from typing import Any


@dataclass
class Note:
    """An Anki note ready for submission via AnkiConnect."""

    model_name: str
    deck_name: str
    fields: dict[str, str]
    tags: list[str] = field(default_factory=list)
    audio: list[dict[str, str]] = field(default_factory=list)
    picture: list[dict[str, str]] = field(default_factory=list)

    def to_ankiconnect(self) -> dict[str, Any]:
        """Serialize to AnkiConnect `addNote` format.

        Returns
        -------
        dict[str, Any]
            Dictionary matching AnkiConnect's `addNote` action params.
        """

        return {
            "deckName": self.deck_name,
            "modelName": self.model_name,
            "fields": self.fields,
            "tags": self.tags,
            "audio": self.audio,
            "picture": self.picture,
        }
