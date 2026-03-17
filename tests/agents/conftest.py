from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from anki_agent.notes.duplicates import DuplicateResult
from anki_agent.settings import Settings

MOCK_SETTINGS = Settings(
    source_language="English",
    target_language="Irish",
    deck="Gaeilge",
    audio_provider="google",
    audio_options={},
)

NEW_RESULT = DuplicateResult(status="new")


@pytest.fixture
def cli_env():
    """Patch CLI dependencies and yield mocks as a namespace."""
    with (
        patch(
            "anki_agent.agents.cli.load_settings",
            return_value=MOCK_SETTINGS,
        ) as m_settings,
        patch("anki_agent.agents.cli.AnkiClient") as m_client_cls,
        patch("anki_agent.agents.cli.ensure_models_exist"),
        patch(
            "anki_agent.agents.cli.check_vocab_duplicate",
            return_value=NEW_RESULT,
        ) as m_dup,
        patch("anki_agent.notes.builder.get_ipa", return_value=None),
        patch(
            "anki_agent.notes.builder.search_image",
            return_value=None,
        ),
        patch(
            "anki_agent.notes.builder.download_image",
            return_value=None,
        ),
    ):
        mock_client = MagicMock()
        m_client_cls.return_value = mock_client

        yield SimpleNamespace(
            settings=m_settings,
            client=mock_client,
            client_cls=m_client_cls,
            dup=m_dup,
        )


@pytest.fixture
def agent_env():
    """Create an AnkiAgent with mock Anki and Anthropic clients."""
    mock_anki = MagicMock()
    mock_anki.model_names.return_value = [
        "AnkiAgent TargetToSource",
        "AnkiAgent SourceToTarget",
        "AnkiAgent Grammar",
        "AnkiAgent Cloze",
    ]
    mock_anthropic = MagicMock()

    with patch(
        "anki_agent.agents.core.load_settings",
        return_value=MOCK_SETTINGS,
    ):
        from anki_agent.agents.core import AnkiAgent

        agent = AnkiAgent(
            anki_client=mock_anki,
            _anthropic_client=mock_anthropic,
        )

    yield SimpleNamespace(
        agent=agent,
        anki=mock_anki,
        anthropic=mock_anthropic,
    )
