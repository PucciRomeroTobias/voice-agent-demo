# Voice Agent demo

Runtime Python de la demo pública de Voice Agent. Este ticket inicial sólo
incluye el pipeline de voz bilingüe y la configuración de sesión; los
escenarios, las herramientas mockeadas, la página web y el endpoint de tokens
se incorporan en los tickets siguientes.

## Requisitos

- Python 3.10 a 3.14.
- [uv](https://docs.astral.sh/uv/) para instalar y ejecutar el proyecto.
- Un proyecto de LiveKit Cloud con las credenciales de `.env.local`.

## Preparación

```sh
cp .env.example .env.local
uv sync
```

Completá `LIVEKIT_URL`, `LIVEKIT_API_KEY` y `LIVEKIT_API_SECRET` solamente en
`.env.local`. Nunca se versionan.

## Probar localmente

El modo `console` usa español por defecto. Para comprobar inglés, cambiá
`VOICE_DEMO_LANGUAGE=en` en `.env.local` antes de iniciar una nueva sesión.

```sh
uv run python src/agent.py console
```

Para usar el agente local desde un cliente de LiveKit, ejecutalo en modo de
desarrollo:

```sh
uv run python src/agent.py dev
```

El nombre de dispatch es fijo: `voice-demo`. Cuando un job traiga metadata
`{"language":"es"}` o `{"language":"en"}`, ese valor prevalece y no cambia
durante la sesión.

## Verificación rápida

```sh
uv run pytest
```
