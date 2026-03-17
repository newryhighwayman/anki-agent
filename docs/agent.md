# Agent Architecture

The agent lives in `anki_agent/agents/` and uses the Anthropic SDK with tool use.

## How it works

1. User sends a message via `AnkiAgent.chat(message)`
2. Claude receives the message with a system prompt describing the language pair
3. Claude decides which tool to call (or asks a clarifying question)
4. The tool is executed (creates cards via NoteBuilder + AnkiClient)
5. The result is sent back to Claude, which formulates a response
6. The loop continues until Claude responds with text (no more tool calls)

## Tools

- `create_vocab_card` — Creates vocabulary flashcards with auto-fetched IPA, audio, and image
- `create_grammar_card` — Creates grammar flashcards
- `create_cloze_card` — Creates cloze deletion flashcards
- `list_decks` — Lists available Anki decks

## Adding new interfaces

To add a new interface (e.g. WhatsApp, Telegram):

1. Create a new file in `agents/` (e.g. `telegram.py`)
2. Import and instantiate `AnkiAgent`
3. Wire up the messaging platform's input/output to `agent.chat(message)`
