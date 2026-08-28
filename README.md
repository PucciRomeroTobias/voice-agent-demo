# Voice Agent demo

Runtime Python de la demo pública de Voice Agent. Incluye el pipeline de voz
bilingüe y tres escenarios mockeados por sesión: Clínica, SaaS B2B y Soporte.
La página web usa un endpoint server-side para emitir tokens de sesión de LiveKit.

## Requisitos

- Python 3.10 a 3.14.
- [uv](https://docs.astral.sh/uv/) para instalar y ejecutar el proyecto.
- Node.js 20 o superior para la página en `web/`.
- Un proyecto de LiveKit Cloud con las credenciales de `.env.local`.

## Preparación

```sh
cp .env.example .env.local
uv sync
cd web && cp .env.example .env.local && npm install
```

Completá `LIVEKIT_URL`, `LIVEKIT_API_KEY` y `LIVEKIT_API_SECRET` en los dos
archivos `.env.local`: el de raíz para el agente Python y `web/.env.local` para
el endpoint que emite tokens. Si más adelante se aloja la web en Vercel, cargá
esas mismas variables sólo como variables de entorno del proyecto. Nunca se
versionan ni se exponen al browser.

## Probar localmente

Para levantar el worker y la web juntos, desde la raíz del repositorio:

```sh
./scripts/dev.sh
```

Desde la carpeta contenedora `contratos-part-time` funciona el mismo comando:

```sh
./scripts/dev.sh
```

El comando comparte en memoria las credenciales de `.env.local` con ambos
procesos y los detiene juntos con `Ctrl+C`. `web/.env.local` es un enlace local
al mismo archivo, por lo que `cd web && npm run dev` también funciona sin
duplicar secretos.

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

## Operación en LiveKit Cloud

El runtime se despliega como agente de LiveKit Cloud en `us-east`. La
configuración versionada vive en `livekit.toml`; el build usa `Dockerfile` y
`.dockerignore`. No incluir `.env.local` ni credenciales en la imagen: LiveKit
inyecta `LIVEKIT_URL`, `LIVEKIT_API_KEY` y `LIVEKIT_API_SECRET` en el runtime.

Antes de desplegar, verificar localmente con los comandos de la sección
anterior. Luego, con la CLI de LiveKit autenticada:

```sh
lk agent status
lk agent logs --log-type deploy
lk agent deploy --secrets-file /dev/null
```

`status` debe mostrar el agente `Running` y los logs deben confirmar el registro
de `voice-demo`. Para volver a la versión previa, primero inspeccionar las
versiones y luego ejecutar el rollback explícito:

```sh
lk agent versions
lk agent rollback --version <version-id>
```
