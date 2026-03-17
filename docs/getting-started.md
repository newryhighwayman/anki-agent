# Getting Started

## Prerequisites

- Python 3.13+
- [Anki](https://apps.ankiweb.net/) desktop app
- [AnkiConnect](https://ankiweb.net/shared/info/2055492159) add-on installed in Anki
- Anki must be running with AnkiConnect enabled (default: `http://127.0.0.1:8765`)

## Installation

```bash
uv sync
```

## Quick Start

### Chat with the agent

```bash
ankiagent chat
```

Then type naturally: "add the word madra (dog) to my Irish deck"

### Create a card directly

```bash
ankiagent vocab madra dog --deck Irish --example "Tá madra agam"
```

### List decks

```bash
ankiagent decks
```
