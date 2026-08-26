# Voice Agent Demo — guía para agentes

## Objetivo del repositorio

Este repositorio contiene la demo pública de un agente de voz bilingüe. Debe
mostrar una conversación fluida en Español o English con LiveKit Cloud, sin
persistencia ni datos personales.

El alcance de producto y las decisiones canónicas se gestionan en Linear. La
implementación local no debe inventar escenarios, integraciones o requisitos
fuera de los tickets activos.

## Mapa del código

- `src/agent.py`: único entrypoint de LiveKit; conserva este path para la CLI y
  el futuro despliegue.
- `src/voice_demo/config.py`: configuración no secreta e inmutable por sesión.
- `tests/`: pruebas rápidas, deterministas y sin red.
- `docs/architecture.md`: límites del runtime y contrato de configuración.
- `CHANGELOG.md`: registro de cambios orientado a usuarios del repositorio.

## Comandos obligatorios antes de entregar un cambio

```sh
uv sync
uv run pytest
uv run ruff check src tests
```

Para comprobar voz real, sólo cuando exista `.env.local` con credenciales
válidas de LiveKit Cloud:

```sh
uv run python src/agent.py console
```

No simules esa verificación ni agregues credenciales de prueba a archivos.

## Reglas de implementación

- Mantener `AGENT_NAME = "voice-demo"` estable. Cambiarlo rompe el dispatch.
- El idioma se elige al comienzo de la sesión y no cambia durante ella.
- Separar prompts, voces y configuración no secreta del entrypoint. Evitar
  abstracciones preventivas: los escenarios mockeados pertenecen a su ticket.
- No registrar ni persistir audio, transcripciones, PII, tokens o secretos.
- Mantener `.env.local` local y actualizar `.env.example` sólo con nombres de
  variables, nunca valores sensibles.
- Escribir pruebas para toda modificación de selección de idioma, metadata o
  configuración de sesión.
- Actualizar `CHANGELOG.md` bajo `Unreleased` para cambios visibles, y
  `docs/architecture.md` si cambia el contrato entre web, token endpoint y
  agente.

## Cómo hacer cambios seguros

1. Leé el ticket activo y estos archivos antes de editar.
2. Hacé el cambio más chico que cumpla el criterio de aceptación.
3. Ejecutá las verificaciones aplicables e informá exactamente cuáles no fueron
   posibles y por qué.
4. No hagas `git commit`, `git push` ni deploy sin autorización explícita.
