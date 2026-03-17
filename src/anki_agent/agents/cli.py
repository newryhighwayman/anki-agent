from __future__ import annotations

import inspect
import json

import click
import questionary

from anki_agent.audio import AUDIO_PROVIDERS, get_audio_provider
from anki_agent.audio.provider import AudioProvider
from anki_agent.client import AnkiClient
from anki_agent.config import SETTINGS_FILE
from anki_agent.languages import LANGUAGES, get_language
from anki_agent.notes.builder import NoteBuilder
from anki_agent.notes.duplicates import check_vocab_duplicate
from anki_agent.notes.note_defs import NoteTypeName
from anki_agent.notes.templates import ensure_models_exist
from anki_agent.settings import Settings, load_settings


def _get_audio_provider(settings: Settings) -> AudioProvider:
    """Build an audio provider from the user's settings."""
    return get_audio_provider(
        settings.audio_provider,
        language_code=settings.target_language_code,
        **settings.audio_options,
    )


@click.group()
def main() -> None:
    """AnkiAgent — AI-powered Anki flashcard creator."""


@main.command()
def init() -> None:
    """Set up AnkiAgent by creating a settings file."""
    click.echo("Welcome to AnkiAgent!")

    language_names = [lang.name for lang in LANGUAGES]
    source_language = questionary.select(
        "What is your source language?",
        choices=language_names,
        default="English",
    ).ask()
    target_language = questionary.select(
        "What language do you want to learn?",
        choices=language_names,
    ).ask()

    language = get_language(target_language)
    available_providers = language.audio_providers
    if len(available_providers) == 1:
        audio_provider = available_providers[0]
        click.echo(f"Audio provider: {audio_provider} (only available provider)")
    else:
        audio_provider = questionary.select(
            "Audio provider",
            choices=list(available_providers),
            default=available_providers[0],
        ).ask()

    audio_options = {}
    provider_cls = AUDIO_PROVIDERS[audio_provider]
    sig = inspect.signature(provider_cls.__init__)

    for param_name, param in sig.parameters.items():
        if param_name == "self":
            continue
        if param_name == "language_code":
            continue
        if param.default is not inspect.Parameter.empty:
            continue

        choices = provider_cls.PARAM_CHOICES.get(param_name, {})
        if choices:
            hint = ", ".join(f"{k} ({v})" for k, v in choices.items())
            click.echo(f"  Options: {hint}")
            value = questionary.select(
                param_name.replace("_", " ").title(),
                choices=list(choices.keys()),
            ).ask()
            audio_options[param_name] = value
        else:
            audio_options[param_name] = click.prompt(
                param_name.replace("_", " ").title()
            )

    deck = click.prompt(
        "What do you want to call your deck?",
        default=language.native_name,
    )

    client = AnkiClient()
    client.create_deck(deck)
    click.echo(f"\nDeck '{deck}' successfully created in Anki.")
    ensure_models_exist(client)

    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "source_language": source_language,
        "target_language": target_language,
        "audio_provider": audio_provider,
        "audio_options": audio_options,
        "deck": deck,
    }
    SETTINGS_FILE.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding="utf-8",
    )

    click.echo(f"\nSettings saved to {SETTINGS_FILE}")


@main.command()
def chat() -> None:
    """Start an interactive chat session with the agent."""
    from anki_agent.agents.core import AnkiAgent

    agent = AnkiAgent()
    click.echo("AnkiAgent chat (type 'quit' to exit)")
    click.echo("-" * 40)

    while True:
        try:
            user_input = click.prompt("You", type=str)
        except (EOFError, KeyboardInterrupt):
            click.echo("\nGoodbye!")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            click.echo("Goodbye!")
            break

        response = agent.chat(user_input)
        click.echo(f"Agent: {response}")


@main.command()
@click.argument("word")
@click.argument("translation")
@click.option("--deck", default=None, help="Anki deck name.")
@click.option("--example", default="", help="Example sentence.")
@click.option("--image", default=None, help="DuckDuckGo search query.")
@click.option("--image-url", default=None, help="Direct image URL.")
@click.option("--audio-url", default=None, help="Direct audio URL.")
@click.option("--no-ipa", is_flag=True, help="Skip IPA lookup.")
@click.option("--no-audio", is_flag=True, help="Skip audio lookup.")
@click.option("--tag", multiple=True, help="Tags for the cards.")
@click.option(
    "--auto-update",
    is_flag=True,
    help="Automatically update duplicates.",
)
def vocab(
    word: str,
    translation: str,
    deck: str | None,
    example: str,
    image: str | None,
    image_url: str | None,
    audio_url: str | None,
    no_ipa: bool,
    no_audio: bool,
    tag: tuple[str, ...],
    auto_update: bool,
) -> None:
    """Create a vocabulary card directly."""
    settings = load_settings()
    deck = deck or settings.deck
    client = AnkiClient()
    ensure_models_exist(client)

    dup = check_vocab_duplicate(
        client, word, NoteTypeName.TARGET_TO_SOURCE, translation
    )

    if dup.status == "duplicate":
        click.echo(
            f"Card for '{word}' already has translation '{translation}' — skipping."
        )
    elif dup.status == "updatable":
        click.echo(f"Card for '{word}' exists with: {dup.existing_translations}")
        if not auto_update and not click.confirm(
            f"Add '{translation}' to existing card?"
        ):
            click.echo("Skipped.")
        else:
            new_translations = f"{dup.existing_translations}<br>{translation}"
            if example:
                new_translations = (
                    f"{dup.existing_translations}<br>{translation} — {example}"
                )
            client.update_note_fields(
                dup.existing_note_id,
                {"Translations": new_translations},
            )
            click.echo(f"Updated existing card for '{word}'.")
    else:
        image_val: str | bool = True
        if image_url:
            image_val = image_url
        elif image:
            image_val = image

        audio_val: str | bool = True
        if audio_url:
            audio_val = audio_url
        elif no_audio:
            audio_val = False

        ipa_val: str | bool = not no_ipa

        audio_provider = _get_audio_provider(settings)
        builder = NoteBuilder(
            deck=deck,
            tags=list(tag),
            audio_provider=audio_provider,
        )
        builder.add_vocab(
            target_word=word,
            source_word=translation,
            example=example,
            ipa=ipa_val,
            image=image_val,
            audio=audio_val,
        )

        notes = builder.build()
        ids = client.add_notes(notes)
        click.echo(f"Created {len(ids)} card(s): {ids}")


@main.command()
@click.argument("rule")
@click.argument("explanation")
@click.argument("example")
@click.option("--deck", default=None, help="Anki deck name.")
@click.option("--tag", multiple=True, help="Tags for the card.")
def grammar(
    rule: str,
    explanation: str,
    example: str,
    deck: str | None,
    tag: tuple[str, ...],
) -> None:
    """Create a grammar card."""
    settings = load_settings()
    deck = deck or settings.deck
    client = AnkiClient()
    ensure_models_exist(client)

    audio_provider = _get_audio_provider(settings)
    builder = NoteBuilder(deck=deck, tags=list(tag), audio_provider=audio_provider)
    builder.add_grammar(rule=rule, explanation=explanation, example=example)

    notes = builder.build()
    ids = client.add_notes(notes)
    click.echo(f"Created {len(ids)} card(s): {ids}")


@main.command()
@click.argument("text")
@click.option("--deck", default=None, help="Anki deck name.")
@click.option("--hint", default="", help="Hint for the cloze card.")
@click.option("--tag", multiple=True, help="Tags for the card.")
def cloze(
    text: str,
    deck: str | None,
    hint: str,
    tag: tuple[str, ...],
) -> None:
    """Create a cloze deletion card."""
    settings = load_settings()
    deck = deck or settings.deck
    client = AnkiClient()
    ensure_models_exist(client)

    audio_provider = _get_audio_provider(settings)
    builder = NoteBuilder(deck=deck, tags=list(tag), audio_provider=audio_provider)
    builder.add_cloze(text=text, hint=hint)

    notes = builder.build()
    ids = client.add_notes(notes)
    click.echo(f"Created {len(ids)} card(s): {ids}")


@main.command()
def decks() -> None:
    """List all Anki decks."""
    client = AnkiClient()
    for name in client.deck_names():
        click.echo(name)
