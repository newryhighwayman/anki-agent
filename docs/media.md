# Media Handling

All media (IPA, images, audio) can be auto-fetched, skipped, or provided directly using the `str | bool` parameter pattern:

| Value | Behavior |
|-------|----------|
| `True` | Auto-find from the default source |
| `False` | Skip — don't include this media |
| `str` | Use directly (URL, search query, or literal value) |

## IPA (`ipa/wiktionary.py`)

Fetches International Phonetic Alphabet pronunciation from Wiktionary's MediaWiki API. Parses the wikitext for `{{IPA|...}}` templates in the target language section.

## Images (`images/`)

- `search.py` — Searches DuckDuckGo Images, returns the top result URL
- `resize.py` — Downloads and resizes images proportionally to `MAX_IMAGE_HEIGHT` (default 200px) using Pillow

For image strings: URLs (starting with "http") are used directly; other strings are used as DuckDuckGo search queries.

## Audio (`audio/scraper.py`)

Fetches audio from focloir.ie using the pattern `{word}_{dialect}.wav` where dialect is one of:
- `u` — Ulster
- `m` — Munster
- `c` — Connacht

The base URL needs to be reverse-engineered from focloir.ie's JavaScript.
