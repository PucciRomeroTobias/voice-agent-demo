# Voice Agent demo para LiveKit

Runtime Python, bilingüe y sin UI, para mostrar el ciclo de un agente de voz
con LiveKit Cloud: STT → LLM → TTS. Incluye tres conversaciones mockeadas por
sesión —Clínica, SaaS B2B y Soporte— y no crea recursos reales.

Cada despliegue pertenece a la cuenta LiveKit de quien lo ejecuta. Este
repositorio no incluye IDs de agentes, subdominios, credenciales ni una web que
emita tokens.

## Qué necesitás

- Python 3.10 a 3.14 y [uv](https://docs.astral.sh/uv/).
- Una cuenta y un proyecto de [LiveKit Cloud](https://cloud.livekit.io/).
- La [CLI de LiveKit](https://docs.livekit.io/reference/developer-tools/livekit-cli/).

LiveKit Cloud inyecta las credenciales de su proyecto en el contenedor. El
runtime usa OpenAI directo para STT, LLM y TTS; `OPENAI_API_KEY` se carga como
secreto del agente y nunca se expone al navegador.

## Ejecutarlo localmente

Cloná el repositorio y prepará el entorno:

```sh
cp .env.example .env.local
uv sync
```

En `.env.local`, cargá las tres credenciales de tu proyecto LiveKit Cloud:

```dotenv
LIVEKIT_URL=wss://<tu-proyecto>.livekit.cloud
LIVEKIT_API_KEY=<tu-api-key>
LIVEKIT_API_SECRET=<tu-api-secret>
```

No subas ese archivo. Para conversar con el agente desde la terminal:

```sh
uv run python src/agent.py console
```

El modo `console` inicia en español y Clínica. Para un cambio puntual, definí
antes de arrancar `VOICE_DEMO_LANGUAGE=en` o `VOICE_DEMO_SCENARIO=support`.

Para exponer el worker local a un cliente LiveKit, usá:

```sh
uv run python src/agent.py dev
```

## Desplegarlo en tu cuenta de LiveKit Cloud

Autenticá la CLI y elegí tu proyecto:

```sh
lk cloud auth
lk project list
lk project set-default "<nombre-de-tu-proyecto>"
```

Desde la raíz de este repositorio, creá el agente una única vez. Elegí la región
que prefieras; el ejemplo usa `us-east`:

```sh
lk agent create --region us-east --secrets-file /dev/null
```

Ese comando registra y despliega tu instancia, y genera `livekit.toml` con el
subdominio e ID de **tu** cuenta. El archivo se ignora a propósito: no lo
commitees ni lo copies a otro proyecto. LiveKit Cloud provee automáticamente
`LIVEKIT_URL`, `LIVEKIT_API_KEY` y `LIVEKIT_API_SECRET` al runtime, por lo que
no deben cargarse como secretos de este agente.

Para desplegar cambios posteriores:

```sh
lk agent deploy --secrets-file /dev/null
lk agent status
lk agent logs --log-type deploy
```

`status` debe informar una réplica `Running` y los logs deben mostrar el
registro de `voice-demo`.

## Probarlo desde Agent Console

En el dashboard de LiveKit, abrí **Agent Console**, seleccioná tu agente y
creá un dispatch explícito. El nombre de dispatch es fijo: `voice-demo`.

La configuración se lee de la **metadata del job/dispatch**, no de la metadata
del participante. Usá JSON válido como estos ejemplos:

```json
{"language":"es","scenario":"clinic"}
{"language":"es","scenario":"saas_b2b"}
{"language":"en","scenario":"support"}
```

Los idiomas permitidos son `es` y `en`; los escenarios son `clinic`,
`saas_b2b` y `support`. Cada combinación fija el prompt, la voz y una sola
herramienta mockeada durante esa sesión. Al completarla, el agente publica un
resumen estructurado en el tópico de datos `voice-demo-result`; no persiste
audio, transcripciones, PII ni resultados.

## Operación y límites

Cada sesión pública termina cuando la persona la finaliza, tras 30 segundos de
inactividad o al llegar al máximo absoluto de dos minutos. El cierre reproduce
una despedida antes de apagar el job.

Para volver a una versión anterior, primero inspeccioná las versiones y luego
indicá explícitamente la que querés restaurar:

```sh
lk agent versions
lk agent rollback --version <version-id>
```

El dashboard de LiveKit muestra estado, errores, uso y límites del proyecto.
Si construís una UI propia, emití tokens del lado servidor y aplicá tus propios
límites de costo, autenticación y protección contra abuso; este repositorio no
incluye esa capa.

## Desarrollo

```sh
uv sync
uv run pytest
uv run ruff check src tests
```

La arquitectura del runtime está documentada en [docs/architecture.md](docs/architecture.md).
