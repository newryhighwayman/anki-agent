from unittest.mock import MagicMock

import pytest

from anki_agent.client import AnkiClient
from anki_agent.notes.note import Note


@pytest.fixture
def client_and_mock():
    """Create an AnkiClient with a mock connector."""
    mock_akc = MagicMock()
    client = AnkiClient(_connector=mock_akc)
    return client, mock_akc


def test_add_note_returns_id(client_and_mock):
    client, mock_akc = client_and_mock
    mock_akc.return_value = 12345

    note = Note(
        model_name="Basic",
        deck_name="Default",
        fields={"Front": "hello", "Back": "world"},
    )
    result = client.add_note(note)

    assert result == 12345
    mock_akc.assert_called_once()


def test_add_notes_returns_ids(client_and_mock):
    client, mock_akc = client_and_mock
    mock_akc.return_value = [1, 2, 3]

    notes = [
        Note(
            model_name="Basic",
            deck_name="Default",
            fields={"Front": f"q{i}", "Back": f"a{i}"},
        )
        for i in range(3)
    ]
    result = client.add_notes(notes)

    assert result == [1, 2, 3]


def test_create_deck(client_and_mock):
    client, mock_akc = client_and_mock
    mock_akc.return_value = 99

    result = client.create_deck("Irish")

    assert result == 99
    mock_akc.assert_called_once_with("createDeck", deck="Irish")


def test_deck_names(client_and_mock):
    client, mock_akc = client_and_mock
    mock_akc.return_value = ["Default", "Irish"]

    result = client.deck_names()

    assert result == ["Default", "Irish"]


def test_find_notes(client_and_mock):
    client, mock_akc = client_and_mock
    mock_akc.return_value = [100, 200]

    result = client.find_notes("Word:madra")

    assert result == [100, 200]
    mock_akc.assert_called_once_with("findNotes", query="Word:madra")


def test_get_notes_info(client_and_mock):
    client, mock_akc = client_and_mock
    mock_akc.return_value = [{"noteId": 100}]

    result = client.get_notes_info([100])

    assert result == [{"noteId": 100}]
    mock_akc.assert_called_once_with("notesInfo", notes=[100])


def test_update_note_fields(client_and_mock):
    client, mock_akc = client_and_mock

    client.update_note_fields(100, {"Front": "updated"})

    mock_akc.assert_called_once_with(
        "updateNoteFields",
        note={"id": 100, "fields": {"Front": "updated"}},
    )
