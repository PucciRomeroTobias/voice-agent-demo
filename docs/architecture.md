# Arquitectura del runtime

## Propósito

El runtime ejecuta el agente de voz de la demo pública sobre LiveKit Cloud. Es
un único agente compartido que, en los tickets siguientes, recibirá escenarios
mockeados desde una configuración permitida.

## Flujo de sesión

```text
Cliente web → endpoint de tokens → room y metadata del job → voice-demo
                                                           ↓
                                                STT → LLM → TTS
```

El endpoint `web/app/api/livekit-token/route.ts` valida la configuración,
genera una room e identidad opacas por sesión y emite un token de participante
válido por diez minutos. El token incluye el dispatch explícito con
`agent_name = voice-demo` y metadata JSON; el navegador recibe únicamente
`server_url` y `participant_token`.

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
dato, lo pregunta y no invoca la herramienta. El endpoint de tokens deberá
rechazar valores fuera de esta lista permitida.

Además de la herramienta propia de cada escenario, cada sesión incorpora
`end_call`. Cuando la persona pide terminar, esta herramienta reproduce una
despedida no interrumpible y luego cierra el job de LiveKit.

## Contrato de resultado para la UI

Luego de ejecutar una herramienta mockeada, el agente publica por el tópico
"voice-demo-result". Su payload contiene escenario, herramientas usadas y el
resultado de negocio. La UI muestra únicamente ese resumen; no recibe prompts,
secretos ni estado interno del agente.

## Límites intencionales

- Sin persistencia, base de datos, PII ni integraciones externas reales.
- Sin secretos en el código ni en archivos versionados.
- Sin cambios de idioma, prompt, voz o herramientas durante una llamada.
- Los mocks viven sólo en memoria por sesión. Cada uno recibe sólo los datos
  obligatorios reunidos durante la conversación, simula el éxito y no crea
  turnos, leads ni casos reales. Devuelve un resultado estructurado con
  escenario, herramientas usadas, datos simulados y resultado para la UI.
- La página web no contiene secretos; el endpoint sólo los lee en el runtime
  server-side mediante `LIVEKIT_URL`, `LIVEKIT_API_KEY` y `LIVEKIT_API_SECRET`.
