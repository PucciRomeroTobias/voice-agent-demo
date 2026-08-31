# Arquitectura del runtime

## Propósito

El runtime ejecuta un único agente de voz sobre LiveKit Cloud. Es una demo
reutilizable: cada instalación pertenece a su propio proyecto LiveKit y se
conecta mediante el dispatch explícito `voice-demo`.

## Flujo de sesión

```text
Cliente o Agent Console → dispatch explícito → room + metadata del job
                                            → voice-demo
                                                ↓
                                     STT → LLM → TTS
```

La creación de rooms, participantes y tokens pertenece al cliente que consume
el runtime; este repositorio no incluye ni requiere una web o endpoint propio.
La metadata JSON del dispatch selecciona una configuración permitida antes de
iniciar la sesión.

## Contrato de metadata

```json
{ "language": "es", "scenario": "clinic" }
```

Los idiomas permitidos son `es` y `en`; los escenarios permitidos son
`clinic`, `saas_b2b` y `support`. La metadata prevalece sobre
`VOICE_DEMO_LANGUAGE`, que es un fallback exclusivo para `console`. La
configuración resultante es inmutable durante toda la sesión, pero `language`
sólo define el idioma inicial del saludo y el orden de las pistas del STT. El
agente responde después en el idioma principal de cada intervención de la
persona y acompaña los cambios entre español e inglés.

El runtime configura al inicio de la sesión el prompt, la voz, los datos de
prueba, la herramienta mockeada y el resultado de negocio de ese escenario.
El prompt tiene una base por idioma —identidad, respuesta apta para voz, flujo,
privacidad y límites de la demo— y un suplemento por escenario. El primer
mensaje es un saludo determinista, humano y abierto, sin mencionar la demo ni
adelantar sus límites. En la primera intervención de la persona, el agente
encuadra el alcance sólo si hace falta y luego continúa con una única pregunta
útil. Si recibe un pedido fuera de foco, no lo resuelve ni cambia de rol: explica
brevemente el alcance y redirige al escenario. Antes de ejecutar una herramienta,
reúne los parámetros obligatorios: fecha y hora para Clínica, necesidad más fecha
y hora para SaaS, y área, impacto y descripción para Soporte. Si falta un dato,
pregunta sólo por ese dato y no invoca la herramienta. Cada mock también puede
recibir `extra_notes` opcionales y no personales —una preferencia o contexto que
la persona ya compartió—; nunca se piden ni publican PII. Los suplementos prohíben consejo médico
y tratan urgencias como fuera de alcance en Clínica; evitan la captura de datos
comerciales en SaaS; y prohíben secretos y acceso a sistemas en Soporte. Un
cliente que emita dispatches debe limitar esos valores a esta lista permitida.

El último bloque del prompt se construye al abrir la sesión con la fecha, hora,
zona IANA `America/Argentina/Buenos_Aires` y un mapa explícito con la próxima
ocurrencia futura de cada día de la semana. El agente resuelve expresiones
relativas no ambiguas —por ejemplo, “mañana” o “el miércoles de la semana que
viene”— contra esas fechas ya calculadas; una fecha absoluta o una semana
identificada explícitamente prevalecen. Los argumentos de fecha se normalizan a
`YYYY-MM-DD`. El reloj y el mapa se calculan una sola vez al construir
`SessionConfig`, quedan embebidos en las instrucciones inmutables y no se
recalculan por turno. Esto preserva el prompt durante la sesión y es suficiente
porque la duración absoluta está limitada a dos minutos. Clínica y SaaS informan
amplia disponibilidad esta semana y la próxima cuando la persona pregunta por
fechas, sin inventar horarios concretos.

Además de la herramienta propia de cada escenario, cada sesión incorpora
`end_call`. Cuando la persona pide terminar, esta herramienta reproduce una
despedida que también puede ser interrumpida y luego cierra el job de LiveKit.

## Ritmo y turnos

El STT usa Deepgram Nova-3 mediante LiveKit Inference con `language="multi"`.
Entrega transcripción streaming, resultados intermedios y alineación por palabra,
y detecta español, inglés y cambios de idioma dentro del mismo stream. El LLM
infiere del texto cuál fue el idioma principal del turno y genera su respuesta
en ese idioma; si la persona cambia, lo acompaña desde la misma respuesta. El
TTS recibe una instrucción neutral que reproduce el idioma del texto generado y
aplica voseo rioplatense cuando éste es español.

El TTS de OpenAI se inicializa con velocidad `1.40` y una instrucción de entrega
ágil, clara y sin muletillas. Las voces se asignan por escenario en ambos
idiomas: `alloy` para Clínica, `echo` para SaaS B2B y `nova` para Soporte. El STT
Deepgram entrega las capacidades que necesita el clasificador adaptativo de
interrupciones de LiveKit, que distingue una interrupción real de un backchannel.
Las respuestas posteriores al saludo, incluso las despedidas, se pueden
interrumpir. El único audio no interrumpible es el saludo inicial, para evitar
que la conexión corte la primera frase.

Para reducir el tiempo de respuesta, `gpt-5.6-luna` recibe
`reasoning.effort="none"`; omitirlo usaría el default `medium` del modelo. El
endpointing es dinámico entre `0.2` y `1.5` segundos, con `alpha=0.7`, y la
generación permite TTS preemptivo. La sesión registra métricas técnicas de EOU,
TTFT del LLM y TTFB del TTS para distinguir el cuello de botella por turno.

`user_away_timeout` cambia el estado de la persona a `away` luego de 7 segundos
de silencio mutuo. El runtime hace dos seguimientos deterministas e
interrumpibles, separados por 7 segundos, y usa el tercer turno para despedirse
y cerrar. Cualquier nuevo estado activo cancela la tarea y reinicia la secuencia;
los mensajes usan el último idioma español o inglés informado por el STT.

## Contrato de resultado

Luego de ejecutar una herramienta mockeada, el runtime confirma oralmente la
gestión en el idioma de la última intervención, publica por el tópico
"voice-demo-result", reproduce la despedida y recién entonces cierra la
sesión. Su payload contiene escenario, herramientas usadas y el resultado de
negocio. Cualquier cliente puede consumir ese resumen, sin recibir prompts,
secretos ni estado interno.

## Observabilidad privada

Al finalizar, `on_session_end` construye una sola vez el `SessionReport` y envía
un artefacto JSON `schema_version=1` al endpoint privado configurado en
`VOICE_OBSERVABILITY_URL`. El bearer token vive únicamente como secreto del
agente y del Worker. El artefacto se indexa por `room_id` —el session ID `RM_…`
de LiveKit— e incluye transcript completo, eventos, tool calls, opciones, uso y
métricas por mensaje, además de idioma y escenario. Antes de enviarlo se eliminan
`audio_recording_path` y `audio_recording_started_at`; no se copia ni persiste
audio.

El destino es el Worker Cloudflare ya existente, que guarda cada sesión en un
Durable Object SQLite privado durante 30 días. Tanto escritura como lectura
requieren el mismo secreto; no hay rutas públicas ni acceso desde el navegador
del visitante. La exportación es best-effort: un fallo se registra, pero no
reabre ni prolonga una llamada ya terminada.

## Límites intencionales

- Sin persistencia de resultados operativos ni integraciones externas reales.
  El transcript puede contener PII aportada espontáneamente y se conserva sólo
  en el almacén privado de observabilidad por 30 días para diagnóstico.
- Sin secretos en el código ni en archivos versionados.
- Sin cambios de prompt, voz ni herramientas durante una llamada. La respuesta
  sí acompaña el idioma detectado en cada turno entre español e inglés.
- Los mocks viven sólo en memoria por sesión. Cada uno recibe sólo los datos
  obligatorios reunidos durante la conversación y, opcionalmente, una nota
  no personal ya compartida. La conversación presenta la gestión como completada
  y no expone lenguaje técnico de simulación; el resumen estructurado publicado a
  la UI conserva explícitamente que no se crearon turnos, leads ni casos reales.
- No contiene una UI, endpoint de tokens ni secretos propios.

## Operación del runtime

LiveKit Cloud ejecuta el contenedor en la región elegida al crearlo. El
`Dockerfile` usa el lockfile de `uv`, ejecuta `src/agent.py start` y corre sin
privilegios. Al ejecutar `lk agent create`, la CLI genera un `livekit.toml` con
el ID y subdominio de la cuenta actual; se ignora para que nunca se comparta.

Las credenciales del proyecto son inyectadas por LiveKit Cloud: el deploy nunca
debe cargar `.env.local` como secretos. El health check operativo es `lk agent
status`; los logs de arranque deben mostrar el registro del worker con
`agent_name: voice-demo`. Ante un deploy defectuoso, `lk agent versions` permite
identificar la versión previa y `lk agent rollback --version <version-id>` la
restaura.
