from unittest.mock import patch

from anki_agent.notes.builder import NoteBuilder


def _noop_get_ipa(word, language=None):

    return None


def _noop_search_image(description):

    return None


def _noop_download_image(url, max_height=200):

    return None


@patch("anki_agent.notes.builder.get_ipa", _noop_get_ipa)
@patch("anki_agent.notes.builder.search_image", _noop_search_image)
@patch("anki_agent.notes.builder.download_image", _noop_download_image)
class TestNoteBuilderVocab:
    def test_single_vocab_produces_two_cards(self):
        builder = NoteBuilder(deck="Test")
        builder.add_vocab("madra", "dog")
        notes = builder.build()

        assert len(notes) == 2
        models = {n.model_name for n in notes}
        assert "AnkiAgent TargetToSource" in models
        assert "AnkiAgent SourceToTarget" in models

    def test_same_target_two_meanings_merges_target_to_source(self):
        builder = NoteBuilder(deck="Test")
        builder.add_vocab("hacer", "to do", example="¿Qué haces?")
        builder.add_vocab("hacer", "to make", example="Hacer una torta")
        notes = builder.build()

        t2s = [n for n in notes if n.model_name == "AnkiAgent TargetToSource"]
        s2t = [n for n in notes if n.model_name == "AnkiAgent SourceToTarget"]

        assert len(t2s) == 1
        assert t2s[0].fields["AnswerCount"] == "2"
        assert "to do" in t2s[0].fields["Translations"]
        assert "to make" in t2s[0].fields["Translations"]

        assert len(s2t) == 2

    def test_same_source_two_targets_merges_source_to_target(self):
        builder = NoteBuilder(deck="Test")
        builder.add_vocab("hacer", "to do")
        builder.add_vocab("realizar", "to do")
        notes = builder.build()

        s2t = [n for n in notes if n.model_name == "AnkiAgent SourceToTarget"]
        assert len(s2t) == 1
        assert s2t[0].fields["AnswerCount"] == "2"
        assert "hacer" in s2t[0].fields["Translations"]
        assert "realizar" in s2t[0].fields["Translations"]

    def test_hacer_realizar_example_produces_four_cards(self):
        builder = NoteBuilder(deck="Spanish")
        builder.add_vocab("hacer", "to do", example="¿Qué haces?")
        builder.add_vocab("hacer", "to make", example="Hacer una torta")
        builder.add_vocab("realizar", "to do", example="Realizar un sueño")
        notes = builder.build()

        assert len(notes) == 4
        t2s = [n for n in notes if n.model_name == "AnkiAgent TargetToSource"]
        s2t = [n for n in notes if n.model_name == "AnkiAgent SourceToTarget"]
        assert len(t2s) == 2
        assert len(s2t) == 2

    def test_media_false_skips(self):
        builder = NoteBuilder(deck="Test")
        builder.add_vocab("madra", "dog", ipa=False, image=False, audio=False)
        notes = builder.build()

        for note in notes:
            assert note.audio == []
            assert note.picture == []
            if "IPA" in note.fields:
                assert note.fields["IPA"] == ""

    def test_media_string_uses_value(self):
        builder = NoteBuilder(deck="Test")
        builder.add_vocab("madra", "dog", ipa="/mˠadˠɾˠə/")
        notes = builder.build()

        t2s = [n for n in notes if n.model_name == "AnkiAgent TargetToSource"]
        assert t2s[0].fields["IPA"] == "/mˠadˠɾˠə/"


@patch("anki_agent.notes.builder.get_ipa", _noop_get_ipa)
@patch("anki_agent.notes.builder.search_image", _noop_search_image)
@patch("anki_agent.notes.builder.download_image", _noop_download_image)
class TestNoteBuilderGrammarCloze:
    def test_grammar_card_passes_through(self):
        builder = NoteBuilder(deck="Test")
        builder.add_grammar(
            rule="Séimhiú",
            explanation="Lenition",
            example="an cat → an chat",
        )
        notes = builder.build()

        assert len(notes) == 1
        assert notes[0].model_name == "AnkiAgent Grammar"
        assert notes[0].fields["Rule"] == "Séimhiú"

    def test_cloze_card_passes_through(self):
        builder = NoteBuilder(deck="Test")
        builder.add_cloze("Tá {{c1::madra}} agam", hint="animal")
        notes = builder.build()

        assert len(notes) == 1
        assert notes[0].model_name == "AnkiAgent Cloze"
        assert "{{c1::madra}}" in notes[0].fields["Text"]
        assert notes[0].fields["Hint"] == "animal"

    def test_mixed_build(self):
        builder = NoteBuilder(deck="Test")
        builder.add_vocab("madra", "dog")
        builder.add_grammar("Séimhiú", "Lenition", "an chat")
        builder.add_cloze("Tá {{c1::madra}} agam")
        notes = builder.build()

        models = [n.model_name for n in notes]
        assert "AnkiAgent TargetToSource" in models
        assert "AnkiAgent SourceToTarget" in models
        assert "AnkiAgent Grammar" in models
        assert "AnkiAgent Cloze" in models
