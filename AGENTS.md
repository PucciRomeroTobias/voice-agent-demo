# Voice Agent Demo

Demo pública bilingüe con LiveKit Cloud. No persistir ni registrar audio,
transcripciones, PII, tokens ni secretos. El alcance canónico vive en Linear:
no inventar requisitos fuera del ticket activo.

- `src/agent.py` es el único entrypoint y `AGENT_NAME = "voice-demo"` no cambia.
- La metadata decide el idioma inicial del saludo. Después, el STT admite
  español e inglés y el agente responde en el idioma de la última intervención.
- El reloj de negocio usa `America/Argentina/Buenos_Aires`; cambios en fechas
  relativas o silencios requieren pruebas deterministas con tiempo inyectado.
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

## Investigación de dirección y diseño

En iniciativas de marca, producto o diseño con impacto alto, antes de investigar
o recomendar referencias, stack o una dirección, crear y mantener un brief vivo
y hacer una entrevista con el usuario. Pedir y analizar sus referencias primero,
hacer una sola pregunta por vez y ajustar la siguiente según la respuesta. Al
entregar, explicar en el mensaje las conclusiones, decisiones, trade-offs y el
próximo paso; un enlace al artefacto no reemplaza esa síntesis.
