# Voice Agent Demo

Demo pública bilingüe con LiveKit Cloud. No persistir ni registrar audio,
transcripciones, PII, tokens ni secretos. El alcance canónico vive en Linear:
no inventar requisitos fuera del ticket activo.

- `src/agent.py` es el único entrypoint y `AGENT_NAME = "voice-demo"` no cambia.
- El idioma se decide al inicio y permanece estable durante la sesión.
- Configuración, prompts y voces se mantienen fuera del entrypoint; usar
  funciones simples y sin abstracciones preventivas.
- `.env.local` es local; `.env.example` sólo contiene nombres de variables.
- Cambios en idioma, metadata o configuración de sesión requieren pruebas.

Antes de entregar un cambio, ejecutar:

```sh
uv sync
uv run pytest
uv run ruff check src tests
```

Sólo con credenciales reales en `.env.local`, se puede verificar voz mediante
`uv run python src/agent.py console`; no simularla.

Documentar sólo cambios durables: arquitectura en `docs/architecture.md`,
hallazgos durables en `docs/research/`, comportamiento en `CHANGELOG.md` y
onboarding en `README.md`. Al cerrar un ticket, registrar resultado y
verificaciones en Linear. Nunca incluir cambios ajenos en commits o pushes;
un deploy exige autorización explícita.
