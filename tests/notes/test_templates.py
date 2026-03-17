from unittest.mock import MagicMock

from anki_agent.notes.templates import ensure_models_exist


def test_ensure_models_creates_missing():
    client = MagicMock()
    client.model_names.return_value = []

    ensure_models_exist(client)

    assert client.create_model.call_count == 4
    names = [c.kwargs["name"] for c in client.create_model.call_args_list]
    assert "AnkiAgent TargetToSource" in names
    assert "AnkiAgent SourceToTarget" in names
    assert "AnkiAgent Grammar" in names
    assert "AnkiAgent Cloze" in names


def test_ensure_models_skips_existing():
    client = MagicMock()
    client.model_names.return_value = [
        "AnkiAgent TargetToSource",
        "AnkiAgent SourceToTarget",
        "AnkiAgent Grammar",
        "AnkiAgent Cloze",
    ]

    ensure_models_exist(client)

    client.create_model.assert_not_called()


def test_template_html_files_readable():
    from anki_agent.notes.templates import _read_resource

    css = _read_resource("css/styles.css")
    assert ".word" in css

    front = _read_resource("target_to_source_front.html")
    assert "{{Word}}" in front
