from anki_agent.notes.note import Note


def test_to_ankiconnect_produces_correct_shape():
    note = Note(
        model_name="Basic",
        deck_name="Default",
        fields={"Front": "hello", "Back": "world"},
        tags=["test"],
        audio=[
            {
                "url": "http://example.com/a.mp3",
                "filename": "a.mp3",
                "fields": ["Front"],
            }
        ],
        picture=[{"data": "abc", "filename": "img.png", "fields": ["Back"]}],
    )

    result = note.to_ankiconnect()

    assert result["deckName"] == "Default"
    assert result["modelName"] == "Basic"
    assert result["fields"] == {"Front": "hello", "Back": "world"}
    assert result["tags"] == ["test"]
    assert len(result["audio"]) == 1
    assert len(result["picture"]) == 1


def test_to_ankiconnect_empty_optionals():
    note = Note(
        model_name="Basic",
        deck_name="Default",
        fields={"Front": "q"},
    )

    result = note.to_ankiconnect()

    assert result["tags"] == []
    assert result["audio"] == []
    assert result["picture"] == []
