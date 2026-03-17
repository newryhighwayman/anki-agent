import logging
from typing import ClassVar
from urllib.parse import quote

import httpx

from anki_agent.audio.provider import AudioProvider

logger = logging.getLogger(__name__)

GOOGLE_TTS_URL = "https://translate.google.com/translate_tts"


class GoogleTranslateAudioProvider(AudioProvider):
    """Audio provider using Google Translate text-to-speech."""

    SUPPORTED_LANGUAGES: ClassVar[frozenset[str]] = frozenset(
        {
            "ar",
            "zh",
            "nl",
            "en",
            "fr",
            "de",
            "it",
            "ja",
            "ko",
            "pl",
            "pt",
            "ru",
            "gd",
            "es",
            "cy",
        }
    )

    def __init__(self, language_code: str = "en") -> None:
        self._language_code = language_code

    def get_audio_url(self, word: str) -> str | None:
        """Return a Google Translate TTS URL for a word.

        Parameters
        ----------
        word : str
            The word or phrase to get audio for.

        Returns
        -------
        str or None
            The TTS URL if reachable, or None.
        """
        url = (
            f"{GOOGLE_TTS_URL}"
            f"?ie=UTF-8"
            f"&q={quote(word)}"
            f"&tl={self._language_code}"
            f"&client=tw-ob"
        )

        try:
            response = httpx.head(url, follow_redirects=True, timeout=5)
            result = url if response.status_code == 200 else None
        except httpx.HTTPError:
            logger.warning("Failed to check Google TTS URL for '%s'", word)
            result = None

        return result
