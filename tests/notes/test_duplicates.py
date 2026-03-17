from unittest.mock import MagicMock

from anki_agent.notes.duplicates import DuplicateResult, check_vocab_duplicate


def _make_client() -> MagicMock:
    return MagicMock()


def test_new_word_returns_new_status():
    client = _make_client()
    client.find_notes.return_value = []

    result = check_vocab_duplicate(client, "madra", "AnkiAgent TargetToSource", "dog")

    assert result.status == "new"
    assert result.existing_note_id is None


def test_exact_duplicate_returns_duplicate_status():
    client = _make_client()
    client.find_notes.return_value = [123]
    client.get_notes_info.return_value = [
        {
            "noteId": 123,
            "fields": {"Translations": {"value": "dog"}},
        }
    ]

    result = check_vocab_duplicate(client, "madra", "AnkiAgent TargetToSource", "dog")

    assert result.status == "duplicate"
    assert result.existing_note_id == 123
    assert result.existing_translations == "dog"


def test_new_translation_returns_updatable_status():
    client = _make_client()
    client.find_notes.return_value = [123]
    client.get_notes_info.return_value = [
        {
            "noteId": 123,
            "fields": {"Translations": {"value": "dog"}},
        }
    ]

    result = check_vocab_duplicate(client, "madra", "AnkiAgent TargetToSource", "hound")

    assert result.status == "updatable"
    assert result.existing_note_id == 123
    assert result.existing_translations == "dog"


def test_duplicate_result_defaults():
    result = DuplicateResult(status="new")

    assert result.existing_note_id is None
    assert result.existing_translations == ""
