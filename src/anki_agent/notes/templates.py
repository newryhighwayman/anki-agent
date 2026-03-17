from importlib import resources

from anki_agent.client import AnkiClient
from anki_agent.notes.note_defs import NOTE_TYPES


def _read_resource(filename: str) -> str:
    """Load a resource file from the templates directory."""
    template_dir = resources.files("anki_agent.notes") / "templates"
    return (template_dir / filename).read_text(encoding="utf-8")


def ensure_models_exist(client: AnkiClient) -> None:
    """Create custom Anki note types if they don't already exist.

    Parameters
    ----------
    client : AnkiClient
        The AnkiConnect client to use.
    """
    existing = client.model_names()
    css = _read_resource("css/styles.css")

    for model_name, config in NOTE_TYPES.items():
        if model_name in existing:
            continue

        card_templates = []
        for tmpl in config["templates"]:
            card_templates.append(
                {
                    "Name": tmpl["Name"],
                    "Front": _read_resource(tmpl["Front"]),
                    "Back": _read_resource(tmpl["Back"]),
                }
            )

        client.create_model(
            name=model_name,
            fields=config["fields"],
            templates=card_templates,
            css=css,
        )
