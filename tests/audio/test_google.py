from unittest.mock import MagicMock, patch

from anki_agent.audio.google import GoogleTranslateAudioProvider


@patch("anki_agent.audio.google.httpx")
def test_returns_url_when_audio_exists(mock_httpx):
    response = MagicMock()
    response.status_code = 200
    mock_httpx.head.return_value = response

    provider = GoogleTranslateAudioProvider(language_code="ga")
    result = provider.get_audio_url("madra")

    assert result is not None
    assert "madra" in result
    assert "tl=ga" in result


@patch("anki_agent.audio.google.httpx")
def test_returns_none_when_unavailable(mock_httpx):
    response = MagicMock()
    response.status_code = 403
    mock_httpx.head.return_value = response

    provider = GoogleTranslateAudioProvider(language_code="ga")
    result = provider.get_audio_url("madra")

    assert result is None
