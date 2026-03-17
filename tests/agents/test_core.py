from unittest.mock import MagicMock, patch

from anki_agent.notes.duplicates import DuplicateResult


def _text_response(text: str) -> MagicMock:
    """Build a mock Anthropic text response."""
    block = MagicMock()
    block.type = "text"
    block.text = text
    response = MagicMock()
    response.content = [block]
    response.stop_reason = "end_turn"

    return response


def _tool_use_response(
    tool_name: str, tool_input: dict, tool_id: str = "t1"
) -> MagicMock:
    """Build a mock Anthropic tool_use response."""
    block = MagicMock()
    block.type = "tool_use"
    block.name = tool_name
    block.input = tool_input
    block.id = tool_id
    response = MagicMock()
    response.content = [block]
    response.stop_reason = "tool_use"

    return response


@patch("anki_agent.agents.core.check_vocab_duplicate")
@patch("anki_agent.notes.builder.get_ipa", return_value=None)
@patch("anki_agent.notes.builder.search_image", return_value=None)
@patch("anki_agent.notes.builder.download_image", return_value=None)
def test_agent_dispatches_vocab_tool(mock_dr, mock_si, mock_fi, mock_dup, agent_env):
    mock_dup.return_value = DuplicateResult(status="new")
    agent_env.anki.add_notes.return_value = [1, 2]

    tool_response = _tool_use_response(
        "create_vocab_card",
        {
            "word": "madra",
            "translations": [{"translation": "dog", "example": "Tá madra agam"}],
            "deck": "Irish",
        },
    )
    text_response = _text_response("Created your card!")

    agent_env.anthropic.messages.create.side_effect = [
        tool_response,
        text_response,
    ]

    result = agent_env.agent.chat("add madra")

    assert "Created your card!" in result
    agent_env.anki.add_notes.assert_called_once()


def test_agent_dispatches_list_decks(agent_env):
    agent_env.anki.deck_names.return_value = ["Default", "Irish"]

    tool_response = _tool_use_response("list_decks", {})
    text_response = _text_response("Here are your decks: Default, Irish")

    agent_env.anthropic.messages.create.side_effect = [
        tool_response,
        text_response,
    ]

    result = agent_env.agent.chat("list decks")

    assert "Default" in result
    agent_env.anki.deck_names.assert_called_once()
