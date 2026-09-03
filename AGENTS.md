# Voice Agent Demo

This is a public bilingual LiveKit Cloud demo. Never persist or log audio, transcripts, personal data, tokens, secrets, private endpoints, or deployment identifiers.

- `src/agent.py` is the only entrypoint and `AGENT_NAME = "voice-demo"` is stable.
- Job metadata chooses the initial greeting language. STT then accepts Spanish and English, and the agent replies in the language of the latest user turn.
- Business time uses `America/Argentina/Buenos_Aires`. Changes to relative dates or silence handling require deterministic tests with injected time.
- Keep configuration, prompts, and voices outside the entrypoint. Prefer simple functions over speculative abstractions.
- `.env.local`, `livekit.toml`, recordings, transcripts, and deployment-specific data stay local and untracked.
- Changes to language, metadata, or session configuration require tests.

Before submitting a change, run:

```bash
uv sync --locked
uv run pytest
uv run ruff check src tests
uv run pip-audit --skip-editable
```

Only verify real voice sessions when you have your own credentials in `.env.local`, using `uv run python src/agent.py console`. Do not simulate successful external calls.

Document durable architecture in `docs/architecture.md`, durable research in `docs/research/`, behavior in `CHANGELOG.md`, and onboarding in `README.md`. Never include unrelated local changes in commits or pushes. A deployment requires explicit authorization.
