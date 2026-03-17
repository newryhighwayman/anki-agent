"""User settings loaded from ~/.ankiagent/settings.json."""

import json
import logging
from dataclasses import dataclass, field

from anki_agent.config import SETTINGS_FILE
from anki_agent.languages import get_language, get_language_code

logger = logging.getLogger(__name__)


@dataclass
class Settings:
    """User-configurable settings for AnkiAgent."""

    target_language: str
    deck: str
    source_language: str = "English"
    audio_provider: str = "google"
    audio_options: dict[str, str] = field(default_factory=dict)

    @property
    def target_language_code(self) -> str:
        """Derive the ISO 639-1 code from `target_language`."""
        return get_language_code(self.target_language)


def load_settings() -> Settings:
    """Load settings from ~/.ankiagent/settings.json.

    Returns
    -------
    Settings
        The user's settings.

    Raises
    ------
    FileNotFoundError
        If the settings file does not exist.
    """
    if not SETTINGS_FILE.exists():
        raise FileNotFoundError(
            f"Settings not found at {SETTINGS_FILE}. "
            "Run 'ankiagent init' to set up AnkiAgent."
        )

    raw = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    target_language = raw["target_language"]
    deck = raw.get("deck", get_language(target_language).native_name)

    return Settings(
        target_language=target_language,
        deck=deck,
        source_language=raw["source_language"],
        audio_provider=raw["audio_provider"],
        audio_options=raw["audio_options"],
    )
