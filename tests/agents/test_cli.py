from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from anki_agent.agents.cli import main
from anki_agent.notes.duplicates import DuplicateResult


def test_vocab_creates_card(cli_env):
    cli_env.client.add_notes.return_value = [1, 2]

    runner = CliRunner()
    result = runner.invoke(main, ["vocab", "madra", "dog", "--deck", "Irish"])

    assert result.exit_code == 0
    assert "Created" in result.output


@patch("anki_agent.agents.cli.AnkiClient")
def test_decks_lists_decks(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    mock_client.deck_names.return_value = ["Default", "Irish"]

    runner = CliRunner()
    result = runner.invoke(main, ["decks"])

    assert result.exit_code == 0
    assert "Default" in result.output
    assert "Irish" in result.output


def test_no_ipa_flag_skips_ipa(cli_env):
    cli_env.client.add_notes.return_value = [1, 2]

    runner = CliRunner()
    result = runner.invoke(main, ["vocab", "madra", "dog", "--no-ipa", "--no-audio"])

    assert result.exit_code == 0
    assert "Created" in result.output


def test_vocab_skips_exact_duplicate(cli_env):
    cli_env.dup.return_value = DuplicateResult(
        status="duplicate",
        existing_note_id=123,
        existing_translations="dog",
    )

    runner = CliRunner()
    result = runner.invoke(main, ["vocab", "madra", "dog"])

    assert result.exit_code == 0
    assert "skipping" in result.output.lower()
    cli_env.client.add_notes.assert_not_called()


def test_vocab_updates_with_auto_update_flag(cli_env):
    cli_env.dup.return_value = DuplicateResult(
        status="updatable",
        existing_note_id=123,
        existing_translations="dog",
    )

    runner = CliRunner()
    result = runner.invoke(main, ["vocab", "madra", "hound", "--auto-update"])

    assert result.exit_code == 0
    assert "Updated" in result.output
    cli_env.client.update_note_fields.assert_called_once()


def test_vocab_prompts_on_updatable(cli_env):
    cli_env.dup.return_value = DuplicateResult(
        status="updatable",
        existing_note_id=123,
        existing_translations="dog",
    )

    runner = CliRunner()
    result = runner.invoke(main, ["vocab", "madra", "hound"], input="n\n")

    assert result.exit_code == 0
    assert "Skipped" in result.output
    cli_env.client.update_note_fields.assert_not_called()


def test_init_creates_settings_file(tmp_path):
    settings_file = tmp_path / "settings.json"

    with patch("anki_agent.agents.cli.SETTINGS_FILE", settings_file):
        runner = CliRunner()
        result = runner.invoke(
            main,
            ["init"],
            input="\nIrish\nu (Ulster)\n\n",
        )

    assert result.exit_code == 0, result.output
    assert settings_file.exists()
    assert "Settings saved" in result.output
