import inspect

from anki_agent.audio.focloir import FocloirAudioProvider
from anki_agent.audio.google import GoogleTranslateAudioProvider
from anki_agent.audio.provider import AudioProvider

AUDIO_PROVIDERS: dict[str, type[AudioProvider]] = {
    "google": GoogleTranslateAudioProvider,
    "focloir": FocloirAudioProvider,
}


def get_audio_provider(name: str, **kwargs) -> AudioProvider:
    """Instantiate an audio provider by name.

    Only keyword arguments accepted by the provider's constructor
    are forwarded; the rest are silently ignored.

    Parameters
    ----------
    name : str
        Provider name (e.g. "google", "focloir").

    **kwargs
        Keyword arguments forwarded to the provider constructor.

    Returns
    -------
    AudioProvider
        The instantiated provider.

    Raises
    ------
    ValueError
        If the provider name is not registered.
    """
    provider_cls = AUDIO_PROVIDERS.get(name)
    if provider_cls is None:
        available = ", ".join(sorted(AUDIO_PROVIDERS))
        raise ValueError(f"Unknown audio provider '{name}'. Available: {available}")

    sig = inspect.signature(provider_cls.__init__)
    accepted = {p.name for p in sig.parameters.values() if p.name != "self"}
    filtered = {k: v for k, v in kwargs.items() if k in accepted}

    return provider_cls(**filtered)


__all__ = [
    "AudioProvider",
    "FocloirAudioProvider",
    "GoogleTranslateAudioProvider",
    "get_audio_provider",
]
