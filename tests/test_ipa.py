from unittest.mock import MagicMock, patch

from anki_agent.ipa import get_ipa

SAMPLE_WIKITEXT = """
==English==
===Pronunciation===
* {{IPA|en|/dɒg/}}

==Irish==
===Pronunciation===
* {{IPA|ga|/mˠadˠɾˠə/}}

===Noun===
{{ga-noun|m|madra|madraí}}
"""

SAMPLE_WIKITEXT_MAITH = """
==Irish==
===Pronunciation===
* {{IPA|ga|/mˠah/}}
"""


@patch("anki_agent.ipa.httpx")
def test_extracts_ipa_from_valid_response(mock_httpx):
    response = MagicMock()
    response.json.return_value = {"parse": {"wikitext": {"*": SAMPLE_WIKITEXT}}}
    response.raise_for_status = MagicMock()
    mock_httpx.get.return_value = response

    result = get_ipa("madra", language="Irish")

    assert result == "/mˠadˠɾˠə/"


@patch("anki_agent.ipa.httpx")
def test_returns_none_when_word_not_found(mock_httpx):
    response = MagicMock()
    response.json.return_value = {"error": {"code": "missingtitle"}}
    response.raise_for_status = MagicMock()
    mock_httpx.get.return_value = response

    result = get_ipa("xyznonexistent", language="Irish")

    assert result is None


@patch("anki_agent.ipa.httpx")
def test_returns_none_when_language_section_missing(mock_httpx):
    response = MagicMock()
    response.json.return_value = {"parse": {"wikitext": {"*": SAMPLE_WIKITEXT}}}
    response.raise_for_status = MagicMock()
    mock_httpx.get.return_value = response

    result = get_ipa("madra", language="Spanish")

    assert result is None


@patch("anki_agent.ipa.httpx")
def test_phrase_tries_full_phrase_first(mock_httpx):
    phrase_wikitext = """
==Irish==
===Pronunciation===
* {{IPA|ga|/phrase_ipa/}}
"""
    response = MagicMock()
    response.json.return_value = {"parse": {"wikitext": {"*": phrase_wikitext}}}
    response.raise_for_status = MagicMock()
    mock_httpx.get.return_value = response

    result = get_ipa("go raibh maith agat", language="Irish")

    assert result == "/phrase_ipa/"
    mock_httpx.get.assert_called_once()


@patch("anki_agent.ipa.httpx")
def test_phrase_falls_back_to_individual_words(mock_httpx):
    not_found = MagicMock()
    not_found.json.return_value = {"error": {"code": "missingtitle"}}
    not_found.raise_for_status = MagicMock()

    madra_response = MagicMock()
    madra_response.json.return_value = {"parse": {"wikitext": {"*": SAMPLE_WIKITEXT}}}
    madra_response.raise_for_status = MagicMock()

    maith_response = MagicMock()
    maith_response.json.return_value = {
        "parse": {"wikitext": {"*": SAMPLE_WIKITEXT_MAITH}}
    }
    maith_response.raise_for_status = MagicMock()

    mock_httpx.get.side_effect = [not_found, madra_response, maith_response]

    result = get_ipa("madra maith", language="Irish")

    assert result == "/mˠadˠɾˠə/ /mˠah/"


@patch("anki_agent.ipa.httpx")
def test_phrase_partial_results(mock_httpx):
    not_found = MagicMock()
    not_found.json.return_value = {"error": {"code": "missingtitle"}}
    not_found.raise_for_status = MagicMock()

    madra_response = MagicMock()
    madra_response.json.return_value = {"parse": {"wikitext": {"*": SAMPLE_WIKITEXT}}}
    madra_response.raise_for_status = MagicMock()

    mock_httpx.get.side_effect = [not_found, madra_response, not_found]

    result = get_ipa("madra xyz", language="Irish")

    assert result == "/mˠadˠɾˠə/"
