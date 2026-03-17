from __future__ import annotations

import base64
from typing import Any

from py_ankiconnect import PyAnkiconnect

from anki_agent.notes.note import Note


class AnkiClient:
    """Wrapper around py-ankiconnect for common Anki operations."""

    def __init__(
        self,
        host: str = "http://127.0.0.1",
        port: int = 8765,
        _connector: PyAnkiconnect | None = None,
    ) -> None:
        self._akc = _connector or PyAnkiconnect(default_host=host, default_port=port)

    def add_note(self, note: Note) -> int:
        """Add a single note to Anki.

        Parameters
        ----------
        note : Note
            The note to add.

        Returns
        -------
        int
            The note ID assigned by Anki.
        """

        return self._akc("addNote", note=note.to_ankiconnect())

    def add_notes(self, notes: list[Note]) -> list[int]:
        """Add multiple notes to Anki.

        Parameters
        ----------
        notes : list of Note
            The notes to add.

        Returns
        -------
        list of int
            The note IDs assigned by Anki.
        """

        return self._akc(
            "addNotes",
            notes=[n.to_ankiconnect() for n in notes],
        )

    def create_deck(self, name: str) -> int:
        """Create a deck if it doesn't exist.

        Parameters
        ----------
        name : str
            The deck name.

        Returns
        -------
        int
            The deck ID.
        """

        return self._akc("createDeck", deck=name)

    def deck_names(self) -> list[str]:
        """List all deck names.

        Returns
        -------
        list of str
            All deck names in Anki.
        """

        return self._akc("deckNames")

    def model_names(self) -> list[str]:
        """List all model (note type) names.

        Returns
        -------
        list of str
            All model names in Anki.
        """

        return self._akc("modelNames")

    def create_model(
        self,
        name: str,
        fields: list[str],
        templates: list[dict[str, str]],
        css: str = "",
    ) -> dict[str, Any]:
        """Create a custom note type in Anki.

        Parameters
        ----------
        name : str
            The model name.

        fields : list of str
            Field names for the model.

        templates : list of dict
            Card templates with "Name", "Front", "Back" keys.

        css : str
            Shared CSS for all cards.

        Returns
        -------
        dict
            The model info returned by AnkiConnect.
        """

        return self._akc(
            "createModel",
            modelName=name,
            inOrderFields=fields,
            cardTemplates=templates,
            css=css,
        )

    def store_media(
        self,
        filename: str,
        *,
        url: str | None = None,
        data: bytes | None = None,
    ) -> str:
        """Store a media file in Anki's media folder.

        Parameters
        ----------
        filename : str
            The filename to store as.

        url : str or None
            URL to download the media from.

        data : bytes or None
            Raw bytes of the media file.

        Returns
        -------
        str
            The filename stored.
        """

        kwargs: dict[str, Any] = {"filename": filename}
        if url:
            kwargs["url"] = url
        elif data:
            kwargs["data"] = base64.b64encode(data).decode()

        return self._akc("storeMediaFile", **kwargs)

    def find_notes(self, query: str) -> list[int]:
        """Find note IDs matching an AnkiConnect query string.

        Parameters
        ----------
        query : str
            AnkiConnect search query
            (e.g. `"Word:madra note:AnkiAgent TargetToSource"`).

        Returns
        -------
        list of int
            Matching note IDs.
        """

        return self._akc("findNotes", query=query)

    def get_notes_info(self, note_ids: list[int]) -> list[dict]:
        """Get detailed info for notes by their IDs.

        Parameters
        ----------
        note_ids : list of int
            The note IDs to look up.

        Returns
        -------
        list of dict
            Note info dicts from AnkiConnect.
        """

        return self._akc("notesInfo", notes=note_ids)

    def update_note_fields(self, note_id: int, fields: dict[str, str]) -> None:
        """Update fields on an existing note.

        Parameters
        ----------
        note_id : int
            The note ID to update.

        fields : dict of str
            Field name to value mapping.
        """
        self._akc(
            "updateNoteFields",
            note={"id": note_id, "fields": fields},
        )
