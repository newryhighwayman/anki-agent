# Workflow

- When in plan mode, always sections on the following:
  - Unit tests - Are new tests needed? Do existing tests need updated?
  - Docs - Are new docs needed? Do the existing docs need updated?

- After making changes to Python files, run `uv run ruff check --fix .` and `uv run ruff format .`.
