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

El endpoint todavía no forma parte de este repositorio. Cuando exista, deberá
iniciar el dispatch explícito con `agent_name = voice-demo` y metadata JSON.

## Contrato actual de metadata

```json
{ "language": "es" }
```

Los únicos valores permitidos hoy son `es` y `en`. La metadata prevalece sobre
`VOICE_DEMO_LANGUAGE`, que es un fallback exclusivo para `console`. La
configuración resultante es inmutable durante toda la sesión.

Los campos futuros de escenario y contexto se validarán en el endpoint de
tokens y se incorporarán sólo en el ticket correspondiente.

## Límites intencionales

- Sin persistencia, base de datos, PII ni integraciones externas reales.
- Sin secretos en el código ni en archivos versionados.
- Sin cambios de idioma, prompt, voz o herramientas durante una llamada.
- Sin página web ni emisión de tokens todavía.
