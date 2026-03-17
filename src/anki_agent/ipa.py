import logging
import re

import httpx

from anki_agent.settings import load_settings

WIKTIONARY_API_URL = "https://en.wiktionary.org/w/api.php"

logger = logging.getLogger(__name__)


def get_ipa(word: str, language: str | None = None) -> str | None:
    """Get IPA pronunciation from Wiktionary.

    Tries the full phrase first. If not found and the input contains
    spaces, looks up each word individually and joins the results.

    Parameters
    ----------
    word : str
        The word or phrase to look up.

    language : str or None
        The language section to search in (e.g. "Irish", "Spanish").
        Defaults to the target language from settings.

    Returns
    -------
    str or None
        The IPA string, or None if not found.
    """
    if language is None:
        language = load_settings().target_language

    result = _get_single_word_ipa(word, language)

    if result is None and " " in word:
        parts = []
        for w in word.split():
            part = _get_single_word_ipa(w, language)
            if part:
                parts.append(part)
        if parts:
            result = " ".join(parts)

    return result


def _get_single_word_ipa(word: str, language: str) -> str | None:
    """Get IPA for a single word from Wiktionary."""
    params = {
        "action": "parse",
        "page": word,
        "prop": "wikitext",
        "format": "json",
    }

    try:
        response = httpx.get(WIKTIONARY_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except (httpx.HTTPError, ValueError):
        logger.warning("Failed to get Wiktionary page for '%s'", word)
        data = None

    if data is None or "error" in data:
        result = None
    else:
        wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
        result = _extract_ipa(wikitext, language)

    return result


def _extract_ipa(wikitext: str, language: str) -> str | None:
    """Extract IPA from a Wiktionary page's wikitext for the given language."""
    lang_pattern = rf"==\s*{re.escape(language)}\s*=="
    lang_match = re.search(lang_pattern, wikitext)

    if lang_match is None:
        result = None
    else:
        section_start = lang_match.end()
        next_lang = re.search(r"\n==[^=]", wikitext[section_start:])
        section_end = section_start + next_lang.start() if next_lang else len(wikitext)
        section = wikitext[section_start:section_end]

        slash_match = re.search(r"\{\{IPA\|[^|]*\|/([^/}]+)/", section)
        bracket_match = re.search(r"\{\{IPA\|[^|]*\|\[([^\]}]+)\]", section)

        if slash_match:
            result = f"/{slash_match.group(1)}/"
        elif bracket_match:
            result = f"[{bracket_match.group(1)}]"
        else:
            result = None

    return result
