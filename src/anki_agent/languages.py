"""Language definitions and lookup utilities."""

from dataclasses import dataclass

from anki_agent.config import AVAILABLE_LANGUAGES


@dataclass(frozen=True)
class Language:
    """A language supported by AnkiAgent."""

    name: str
    iso_code: str
    native_name: str
    audio_providers: tuple[str, ...]


LANGUAGES = tuple(Language(**entry) for entry in AVAILABLE_LANGUAGES)
_LANGUAGE_BY_NAME = {lang.name: lang for lang in LANGUAGES}


def get_language(name: str) -> Language:
    """Look up a language by its English name.

    Parameters
    ----------
    name : str
        Full language name (e.g. "Irish", "Spanish").

    Returns
    -------
    Language
        The matching `Language` object.

    Raises
    ------
    ValueError
        If the language is not in the known mapping.
    """
    lang = _LANGUAGE_BY_NAME.get(name)
    if lang is None:
        available = ", ".join(sorted(_LANGUAGE_BY_NAME))
        raise ValueError(f"Unknown language '{name}'. Known languages: {available}")

    return lang


def get_language_code(language: str) -> str:
    """Map a language name to its ISO 639-1 code.

    Parameters
    ----------
    language : str
        Full language name (e.g. "Irish", "Spanish").

    Returns
    -------
    str
        The two-letter ISO 639-1 code.

    Raises
    ------
    ValueError
        If the language is not in the known mapping.
    """
    return get_language(language).iso_code


def get_available_languages() -> tuple[Language, ...]:
    """Return all supported languages.

    Returns
    -------
    tuple of Language
        All languages supported by AnkiAgent.
    """
    return LANGUAGES
