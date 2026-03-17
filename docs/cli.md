# CLI Reference

## Commands

### `ankiagent chat`

Interactive chat session with the Claude-powered agent. The agent can translate, look up media, and create cards conversationally.

### `ankiagent vocab <word> <translation>`

Create a vocabulary card directly (bypasses the agent).

Options:
- `--deck` — Anki deck name (default: "Default")
- `--example` — Example sentence
- `--image "desc"` — DuckDuckGo search query for the card image
- `--image-url <url>` — Use a specific image URL directly
- `--audio-url <url>` — Use a specific audio URL directly
- `--no-ipa` — Skip IPA pronunciation lookup
- `--no-audio` — Skip audio lookup
- `--tag` — Add tags (repeatable)

### `ankiagent grammar <rule> <explanation> <example>`

Create a grammar card.

Options:
- `--deck` — Anki deck name (default: "Default")
- `--tag` — Add tags (repeatable)

### `ankiagent cloze <text>`

Create a cloze deletion card. Use `{{c1::word}}` syntax in the text.

Options:
- `--deck` — Anki deck name (default: "Default")
- `--hint` — Hint shown on the front
- `--tag` — Add tags (repeatable)

### `ankiagent decks`

List all available Anki decks.
