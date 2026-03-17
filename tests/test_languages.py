import pytest

from anki_agent.audio import AUDIO_PROVIDERS
from anki_agent.languages import (
    LANGUAGES,
    Language,
    get_available_languages,
    get_language,
    get_language_code,
)


def test_get_language_returns_language():
    lang = get_language("Irish")

    assert isinstance(lang, Language)
    assert lang.iso_code == "ga"
    assert lang.native_name == "Gaeilge"


def test_get_language_unknown_raises():
    with pytest.raises(ValueError, match="Unknown language"):
        get_language("Klingon")


def test_get_language_code_delegates():
    assert get_language_code("Spanish") == "es"


def test_get_available_languages_returns_all():
    result = get_available_languages()

    assert result is LANGUAGES
    assert len(result) == 16


def test_irish_only_has_focloir_provider():
    lang = get_language("Irish")

    assert lang.audio_providers == ("focloir",)
    assert "google" not in lang.audio_providers


def test_all_audio_providers_are_registered():
    for lang in LANGUAGES:
        for provider_key in lang.audio_providers:
            assert provider_key in AUDIO_PROVIDERS, (
                f"{lang.name} references unknown provider '{provider_key}'"
            )
