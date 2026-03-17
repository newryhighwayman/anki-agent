from abc import ABC, abstractmethod
from typing import ClassVar


class AudioProvider(ABC):
    """Base class for audio providers."""

    SUPPORTED_LANGUAGES: ClassVar[frozenset[str]]
    PARAM_CHOICES: ClassVar[dict[str, dict[str, str]]] = {}

    @abstractmethod
    def get_audio_url(self, word: str) -> str | None:
        """Return the audio URL for a word, or None if unavailable.

        Parameters
        ----------
        word : str
            The word to get audio for.

        Returns
        -------
        str or None
            The audio URL, or None if not found.
        """
