import json

import pytest

from anki_agent.languages import get_language_code
from anki_agent.settings import Settings, load_settings


def test_get_language_code_known():
    assert get_language_code("Irish") == "ga"
    assert get_language_code("Spanish") == "es"


def test_get_language_code_unknown_raises():
    with pytest.raises(ValueError, match="Unknown language"):
        get_language_code("Klingon")


def test_load_settings_reads_json(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
        json.dumps(
            {
                "source_language": "French",
                "target_language": "Spanish",
                "audio_provider": "google",
                "audio_options": {},
                "deck": "Español",
            }
        )
    )
    monkeypatch.setattr("anki_agent.settings.SETTINGS_FILE", settings_file)

    result = load_settings()

    assert result.source_language == "French"
    assert result.target_language == "Spanish"
    assert result.deck == "Español"


def test_load_settings_defaults_deck_to_native_name(tmp_path, monkeypatch):
    settings_file = tmp_path / "settings.json"
    settings_file.write_text(
        json.dumps(
            {
                "source_language": "English",
                "target_language": "Spanish",
                "audio_provider": "google",
                "audio_options": {},
            }
        )
    )
    monkeypatch.setattr("anki_agent.settings.SETTINGS_FILE", settings_file)

    result = load_settings()

    assert result.deck == "Español"


def test_load_settings_raises_when_no_file(tmp_path, monkeypatch):
    missing = tmp_path / "nope.json"
    monkeypatch.setattr("anki_agent.settings.SETTINGS_FILE", missing)

    with pytest.raises(FileNotFoundError, match="ankiagent init"):
        load_settings()


def test_target_language_code_property():
    s = Settings(target_language="Irish", deck="Gaeilge")

    assert s.target_language_code == "ga"


def test_settings_defaults():
    s = Settings(target_language="Spanish", deck="Español")

    assert s.source_language == "English"
    assert s.target_language == "Spanish"
    assert s.audio_provider == "google"
    assert s.audio_options == {}
    assert s.deck == "Español"
