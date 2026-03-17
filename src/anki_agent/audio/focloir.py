import logging
from typing import ClassVar

import httpx

from anki_agent.audio.provider import AudioProvider

logger = logging.getLogger(__name__)


class FocloirAudioProvider(AudioProvider):
    """Audio provider for Irish using focloir.ie."""

    SUPPORTED_LANGUAGES: ClassVar[frozenset[str]] = frozenset({"ga"})

    DIALECTS: ClassVar[dict[str, str]] = {
        "u": "Ulster",
        "m": "Munster",
        "c": "Connacht",
    }

    PARAM_CHOICES: ClassVar[dict[str, dict[str, str]]] = {
        "dialect": DIALECTS,
    }

    def __init__(
        self,
        dialect: str,
        base_url: str = "https://www.focloir.ie",
    ) -> None:
        if dialect not in self.DIALECTS:
            available = ", ".join(f"{k} ({v})" for k, v in self.DIALECTS.items())
            raise ValueError(
                f"Unknown Irish dialect '{dialect}'. Available: {available}"
            )
        self._base_url = base_url
        self._dialect = dialect

    def get_audio_url(self, word: str) -> str | None:
        """Return the focloir.ie audio URL for a word.

        Parameters
        ----------
        word : str
            The Irish word to get audio for.

        Returns
        -------
        str or None
            The audio URL if it exists, or None.
        """
        filename = f"{word}_{self._dialect}.wav"
        url = f"{self._base_url}/media/audio/{filename}"

        try:
            response = httpx.head(url, follow_redirects=True, timeout=5)
            result = url if response.status_code == 200 else None
        except httpx.HTTPError:
            logger.warning("Failed to check audio URL for '%s'", word)
            result = None

        return result
