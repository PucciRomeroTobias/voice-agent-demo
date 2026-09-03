# Contributing

Thanks for helping improve the LiveKit voice agent demo. Bug fixes, tests, accessibility improvements, documentation, and careful latency or reliability work are welcome.

## Before opening a pull request

1. Open an issue first for large behavioral or architecture changes.
2. Never commit credentials, tokens, deployment URLs, room or project identifiers, transcripts, recordings, or generated `livekit.toml` files.
3. Keep the three business scenarios demonstrative: tools must remain in-memory mocks and must not request personal data.
4. Add deterministic tests for changes to language handling, metadata, timing, prompts, or session configuration.

## Local checks

```bash
uv sync --locked
uv run ruff check src tests
uv run pytest
uv run pip-audit --skip-editable
```

Pull requests should explain the motivation, describe observable behavior changes, and call out cost, privacy, or latency trade-offs.
