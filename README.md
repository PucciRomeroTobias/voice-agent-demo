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
runtime usa Deepgram Nova-3 multilingual mediante LiveKit Inference para STT y
OpenAI directo para LLM y TTS; `OPENAI_API_KEY` se carga como secreto del agente
y nunca se expone al navegador.

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

El modo `console` inicia con saludo en español y escenario Clínica. Para un
cambio puntual, definí antes de arrancar `VOICE_DEMO_LANGUAGE=en` o
`VOICE_DEMO_SCENARIO=support`. El idioma inicial no bloquea la conversación: el
agente responde en español o inglés según la última intervención de la persona.

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
`saas_b2b` y `support`. `language` elige el saludo inicial, pero el STT escucha
ambos idiomas y el agente acompaña el idioma de la persona en cada turno. Cada
combinación fija el prompt, la voz y una sola herramienta mockeada durante esa
sesión. Al completarla, el agente publica un resumen estructurado en el tópico
de datos `voice-demo-result`.

Cuando `VOICE_OBSERVABILITY_URL` y `VOICE_OBSERVABILITY_TOKEN` están
configurados, `on_session_end` envía al Worker privado el transcript completo,
tool calls, eventos y métricas por turno, indexados por el `room_id` `RM_…`.
Nunca sube audio ni su ruta local. El Worker autentica la escritura y lectura y
elimina el artefacto a los 30 días. Esta persistencia se usa exclusivamente para
diagnóstico; los resultados de Clínica, SaaS y Soporte siguen siendo mockeados y
no crean recursos reales.

## Operación y límites

Cada sesión pública termina cuando la persona la finaliza, al llegar al máximo
absoluto de dos minutos o después de tres turnos consecutivos sin respuesta. Tras
7 segundos de silencio mutuo, el agente hace un primer seguimiento; repite el
seguimiento 7 segundos después y cierra con una despedida en el tercer turno,
aproximadamente a los 21 segundos. Si la persona vuelve a hablar, la secuencia se
cancela y el conteo vuelve a empezar.

Al iniciar cada sesión, el prompt recibe la fecha y hora local de
`America/Argentina/Buenos_Aires` y un calendario precalculado de la semana actual
y la siguiente. El agente interpreta contra ese mapa frases como “mañana” o “el
miércoles de la semana que viene”, considerando semanas de lunes a domingo, y
normaliza las fechas a `YYYY-MM-DD` antes de usar una herramienta. Sólo pide
aclaración cuando falta la hora o la expresión es realmente ambigua.

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
