from __future__ import annotations

import base64
import logging
from dataclasses import dataclass
from typing import Self

from anki_agent.audio.provider import AudioProvider
from anki_agent.images import download_image, resize_image, search_image
from anki_agent.ipa import get_ipa
from anki_agent.notes.note import Note
from anki_agent.notes.note_defs import NoteTypeName

logger = logging.getLogger(__name__)


@dataclass
class _VocabEntry:
    target_word: str
    source_word: str
    example: str
    ipa: str | bool
    image: str | bool
    audio: str | bool


@dataclass
class _GrammarEntry:
    rule: str
    explanation: str
    example: str
    ipa: str | bool
    image: str | bool
    audio: str | bool


@dataclass
class _ClozeEntry:
    text: str
    hint: str
    ipa: str | bool
    image: str | bool
    audio: str | bool


class NoteBuilder:
    """Builds Anki notes with deduplication for multi-meaning vocab.

    Examples
    --------
    >>> builder = NoteBuilder(deck="Spanish", audio_provider=provider)
    >>> notes = (
    ...     builder
    ...     .add_vocab("perro", "dog", example="El perro corre.")
    ...     .add_vocab("gato", "cat")
    ...     .build()
    ... )
    """

    def __init__(
        self,
        deck: str = "Default",
        tags: list[str] | None = None,
        audio_provider: AudioProvider | None = None,
    ) -> None:
        self._deck = deck
        self._tags = tags or []
        self._audio_provider = audio_provider
        self._vocab: list[_VocabEntry] = []
        self._grammar: list[_GrammarEntry] = []
        self._cloze: list[_ClozeEntry] = []

    def add_vocab(
        self,
        target_word: str,
        source_word: str,
        *,
        example: str = "",
        ipa: str | bool = True,
        image: str | bool = True,
        audio: str | bool = True,
    ) -> Self:
        """Add a vocab mapping (target <-> source).

        Parameters
        ----------
        target_word : str
            Word in the target language.

        source_word : str
            Translation in the source language.

        example : str
            Example sentence using `target_word`.

        ipa : str or bool
            IPA pronunciation. `True` = auto-fetch from Wiktionary,
            `False` = skip, str = use this literal IPA string directly.

        image : str or bool
            `True` = auto-search DuckDuckGo Images using the word as query,
            `False` = skip, str = if starts with "http" use as direct URL, otherwise use
            as a DuckDuckGo search query (e.g. `"brown dog"`).

        audio : str or bool
            `True` = auto-fetch audio, `False` = skip, str = use this URL directly.

        Returns
        -------
        Self
            The builder instance for chaining.
        """
        self._vocab.append(
            _VocabEntry(
                target_word=target_word,
                source_word=source_word,
                example=example,
                ipa=ipa,
                image=image,
                audio=audio,
            )
        )

        return self

    def add_grammar(
        self,
        rule: str,
        explanation: str,
        example: str,
        *,
        ipa: str | bool = True,
        image: str | bool = True,
        audio: str | bool = True,
    ) -> Self:
        """Add a grammar card.

        Parameters
        ----------
        rule : str
            The grammar rule.

        explanation : str
            Explanation of the rule.

        example : str
            Example sentence demonstrating the rule.

        ipa : str or bool
            IPA pronunciation. `True` = auto-fetch from Wiktionary, `False` = skip,
            str = use this literal IPA string directly.

        image : str or bool
            `True` = auto-search DuckDuckGo Images using the word as query,
            `False` = skip, str = if starts with "http" use as direct URL, otherwise use
            as a DuckDuckGo search query (e.g. `"brown dog"`).

        audio : str or bool
            `True` = auto-fetch audio, `False` = skip, str = use this URL directly.

        Returns
        -------
        Self
            The builder instance for chaining.
        """
        self._grammar.append(
            _GrammarEntry(
                rule=rule,
                explanation=explanation,
                example=example,
                ipa=ipa,
                image=image,
                audio=audio,
            )
        )

        return self

    def add_cloze(
        self,
        text: str,
        *,
        hint: str = "",
        ipa: str | bool = True,
        image: str | bool = True,
        audio: str | bool = True,
    ) -> Self:
        """Add a cloze card.

        Parameters
        ----------
        text : str
            Cloze text using `{{c1::word}}` syntax.

        hint : str
            Optional hint shown on the front of the card.

        ipa : str or bool
            IPA pronunciation. `True` = auto-fetch from Wiktionary, `False` = skip,
            str = use this literal IPA string directly.

        image : str or bool
            `True` = auto-search DuckDuckGo Images using the word as query,
            `False` = skip, str = if starts with "http" use as direct URL, otherwise use
            as a DuckDuckGo search query (e.g. `"brown dog"`).

        audio : str or bool
            `True` = auto-fetch audio, `False` = skip, str = use this URL directly.

        Returns
        -------
        Self
            The builder instance for chaining.
        """
        self._cloze.append(
            _ClozeEntry(
                text=text,
                hint=hint,
                ipa=ipa,
                image=image,
                audio=audio,
            )
        )

        return self

    def build(self) -> list[Note]:
        """Build all cards, merging multi-meaning vocab words.

        Returns
        -------
        list of Note
            1 TargetToSource per unique target word,
            1 SourceToTarget per unique source word,
            plus grammar and cloze cards as-is.
        """
        notes = []
        notes.extend(self._build_vocab())
        notes.extend(self._build_grammar())
        notes.extend(self._build_cloze())

        return notes

    def _resolve_ipa(self, ipa: str | bool, word: str) -> str:
        """Resolve an IPA value to a string, getting it from Wiktionary if needed."""
        if ipa is False:
            result = ""
        elif isinstance(ipa, str):
            result = ipa
        else:
            result = get_ipa(word) or ""

        return result

    def _resolve_image(self, image: str | bool, word: str) -> dict | None:
        """Resolve an image value to a media dict, searching and downloading."""
        if image is False:
            result = None
        else:
            if isinstance(image, str):
                url = image if image.startswith("http") else search_image(image)
            else:
                url = search_image(word)

            raw_bytes = download_image(url) if url else None

            if raw_bytes is None:
                result = None
            else:
                image_bytes = resize_image(raw_bytes)
                encoded = base64.b64encode(image_bytes).decode()
                filename = f"{word.replace(' ', '_')}.png"
                result = {
                    "data": encoded,
                    "filename": filename,
                    "fields": ["Image"],
                }

        return result

    def _resolve_audio(self, audio: str | bool, word: str) -> dict | None:
        """Resolve an audio value to a media dict, getting the URL if needed."""
        if audio is False or self._audio_provider is None:
            result = None
        else:
            if isinstance(audio, str):
                url = audio
            else:
                url = self._audio_provider.get_audio_url(word)

            if not url:
                result = None
            else:
                filename = f"{word.replace(' ', '_')}.wav"
                result = {
                    "url": url,
                    "filename": filename,
                    "fields": ["Word"],
                }

        return result

    def _build_vocab(self) -> list[Note]:
        """Build vocab notes, merging entries that share a target or source word."""
        target_groups: dict[str, list[_VocabEntry]] = {}
        for entry in self._vocab:
            target_groups.setdefault(entry.target_word, []).append(entry)

        source_groups: dict[str, list[_VocabEntry]] = {}
        for entry in self._vocab:
            source_groups.setdefault(entry.source_word, []).append(entry)

        notes = []

        for target_word, entries in target_groups.items():
            first = entries[0]
            ipa_str = self._resolve_ipa(first.ipa, target_word)
            translations = []
            for e in entries:
                line = e.source_word
                if e.example:
                    line += f" — {e.example}"
                translations.append(line)

            fields = {
                "Word": target_word,
                "IPA": ipa_str,
                "AnswerCount": str(len(entries)),
                "Translations": "<br>".join(translations),
                "Image": "",
            }

            note = Note(
                model_name=NoteTypeName.TARGET_TO_SOURCE,
                deck_name=self._deck,
                fields=fields,
                tags=list(self._tags),
            )

            picture = self._resolve_image(first.image, target_word)
            if picture:
                note.picture.append(picture)

            audio_data = self._resolve_audio(first.audio, target_word)
            if audio_data:
                note.audio.append(audio_data)

            notes.append(note)

        for source_word, entries in source_groups.items():
            translations = []
            for e in entries:
                ipa_str = self._resolve_ipa(e.ipa, e.target_word)
                line = e.target_word
                if ipa_str:
                    line += f" [{ipa_str}]"
                if e.example:
                    line += f" — {e.example}"
                translations.append(line)

            first = entries[0]
            fields = {
                "Word": source_word,
                "AnswerCount": str(len(entries)),
                "Translations": "<br>".join(translations),
                "Image": "",
            }

            note = Note(
                model_name=NoteTypeName.SOURCE_TO_TARGET,
                deck_name=self._deck,
                fields=fields,
                tags=list(self._tags),
            )

            picture = self._resolve_image(first.image, source_word)
            if picture:
                note.picture.append(picture)

            notes.append(note)

        return notes

    def _build_grammar(self) -> list[Note]:
        """Build grammar notes from stored entries."""
        notes = []
        for entry in self._grammar:
            ipa_str = self._resolve_ipa(entry.ipa, entry.rule)
            fields = {
                "Rule": entry.rule,
                "Explanation": entry.explanation,
                "Example": entry.example,
                "IPA": ipa_str,
                "Image": "",
            }

            note = Note(
                model_name=NoteTypeName.GRAMMAR,
                deck_name=self._deck,
                fields=fields,
                tags=list(self._tags),
            )

            picture = self._resolve_image(entry.image, entry.rule)
            if picture:
                note.picture.append(picture)

            audio_data = self._resolve_audio(entry.audio, entry.rule)
            if audio_data:
                note.audio.append(audio_data)

            notes.append(note)

        return notes

    def _build_cloze(self) -> list[Note]:
        """Build cloze deletion notes from stored entries."""
        notes = []
        for entry in self._cloze:
            ipa_str = self._resolve_ipa(entry.ipa, entry.text)
            fields = {
                "Text": entry.text,
                "Hint": entry.hint,
                "IPA": ipa_str,
                "Image": "",
            }

            note = Note(
                model_name=NoteTypeName.CLOZE,
                deck_name=self._deck,
                fields=fields,
                tags=list(self._tags),
            )

            picture = self._resolve_image(entry.image, entry.text)
            if picture:
                note.picture.append(picture)

            audio_data = self._resolve_audio(entry.audio, entry.text)
            if audio_data:
                note.audio.append(audio_data)

            notes.append(note)

        return notes
