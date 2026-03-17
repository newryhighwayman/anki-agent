from unittest.mock import MagicMock, patch

from anki_agent.audio.focloir import FocloirAudioProvider


@patch("anki_agent.audio.focloir.httpx")
def test_returns_url_when_audio_exists(mock_httpx):
    response = MagicMock()
    response.status_code = 200
    mock_httpx.head.return_value = response

    provider = FocloirAudioProvider(dialect="u")
    result = provider.get_audio_url("madra")

    assert result is not None
    assert "madra_u.wav" in result


@patch("anki_agent.audio.focloir.httpx")
def test_returns_none_when_audio_not_found(mock_httpx):
    response = MagicMock()
    response.status_code = 404
    mock_httpx.head.return_value = response

    provider = FocloirAudioProvider(dialect="u")
    result = provider.get_audio_url("xyznonexistent")

    assert result is None
