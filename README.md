# Voice Agent demo

Runtime Python de la demo pública de Voice Agent. Incluye el pipeline de voz
bilingüe y tres escenarios mockeados por sesión: Clínica, SaaS B2B y Soporte.
La página web usa el endpoint de tokens que se incorpora en el ticket siguiente.

## Requisitos

- Python 3.10 a 3.14.
- [uv](https://docs.astral.sh/uv/) para instalar y ejecutar el proyecto.
- Node.js 20 o superior para la página en `web/`.
- Un proyecto de LiveKit Cloud con las credenciales de `.env.local`.

## Preparación

```sh
cp .env.example .env.local
uv sync
cd web && npm install
```

Completá `LIVEKIT_URL`, `LIVEKIT_API_KEY` y `LIVEKIT_API_SECRET` solamente en
`.env.local`. Nunca se versionan.

## Probar localmente

El modo `console` usa español y Clínica por defecto. Para comprobar otro
idioma o escenario, cambiá `VOICE_DEMO_LANGUAGE=en` o
`VOICE_DEMO_SCENARIO=support` en `.env.local` antes de iniciar una nueva
sesión. En dispatch, la metadata
`{"language":"es","scenario":"support"}` prevalece sobre esos fallbacks.

```sh
uv run python src/agent.py console
```

Para usar el agente local desde un cliente de LiveKit, ejecutalo en modo de
desarrollo:

```sh
uv run python src/agent.py dev
```

El nombre de dispatch es fijo: `voice-demo`. Cada job recibe `language` y
`scenario` al inicio; sólo se aceptan `clinic`, `saas_b2b` y `support`.
El escenario fija el prompt, la voz y una única herramienta mockeada. Su
resultado estructurado no persiste y queda disponible para que la futura UI
muestre el resumen final.

## Verificación rápida

```sh
uv run pytest
cd web && npm run lint && npm run build
```
