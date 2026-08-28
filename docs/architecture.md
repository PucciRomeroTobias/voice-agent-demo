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
configuración resultante es inmutable durante toda la sesión.

El runtime configura al inicio de la sesión el prompt, la voz, los datos de
prueba, la herramienta mockeada y el resultado de negocio de ese escenario.
El primer mensaje es una presentación determinista del rol del agente y hace la
primera pregunta útil. Antes de ejecutar una herramienta, el agente reúne los
parámetros obligatorios del escenario: fecha y hora para Clínica, necesidad más
fecha y hora para SaaS, y área, impacto y descripción para Soporte. Si falta un
dato, lo pregunta y no invoca la herramienta. Un cliente que emita dispatches
debe limitar esos valores a esta lista permitida.

Además de la herramienta propia de cada escenario, cada sesión incorpora
`end_call`. Cuando la persona pide terminar, esta herramienta reproduce una
despedida no interrumpible y luego cierra el job de LiveKit.

## Contrato de resultado

Luego de ejecutar una herramienta mockeada, el agente publica por el tópico
"voice-demo-result". Su payload contiene escenario, herramientas usadas y el
resultado de negocio. Cualquier cliente puede consumir ese resumen, sin recibir
prompts, secretos ni estado interno.

## Límites intencionales

- Sin persistencia, base de datos, PII ni integraciones externas reales.
- Sin secretos en el código ni en archivos versionados.
- Sin cambios de idioma, prompt, voz o herramientas durante una llamada.
- Los mocks viven sólo en memoria por sesión. Cada uno recibe sólo los datos
  obligatorios reunidos durante la conversación, simula el éxito y no crea
  turnos, leads ni casos reales. Devuelve un resultado estructurado con
  escenario, herramientas usadas, datos simulados y resultado para la UI.
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
