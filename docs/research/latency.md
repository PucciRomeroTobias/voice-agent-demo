# Latencia conversacional

Investigación realizada el 2026-08-30 para PRO-24.

## Evidencia de la sesión desplegada

Los logs de las dos últimas sesiones disponibles mostraron repetidamente que la
detección adaptativa de interrupciones era incompatible con la configuración y
se deshabilitaba. La inspección del plugin instalado confirmó que
`gpt-transcribe` expone STT no-streaming, sin resultados intermedios ni
timestamps alineados. LiveKit requiere VAD, STT streaming y transcript alineado
para su clasificador adaptativo; con este STT corresponde declarar interrupción
por VAD.

La versión desplegada no registraba métricas por etapa, de modo que esos logs no
permiten atribuir una demora concreta a EOU, LLM o TTS. LiveKit define la latencia
conversacional aproximada como:

```text
EOU delay + LLM TTFT + TTS TTFB
```

La implementación incorpora `metrics_collected` para registrar esos valores en
las próximas pruebas, sin conservar audio ni transcripciones.

## Ajustes elegidos

- `gpt-5.6-luna`: `reasoning.effort="none"`. OpenAI documenta que el default es
  `medium`; `none` es el valor explícito para desactivar reasoning.
- Endpointing dinámico: mínimo `0.2` s, máximo `1.5` s y `alpha=0.7`.
- Generación preemptiva habilitada, incluido TTS preemptivo.
- Deepgram Nova-3 multilingual mediante LiveKit Inference: STT streaming con
  resultados intermedios y alineación por palabra. Esto permite solapar la
  transcripción con el habla y usar interrupción adaptativa.

El reloj temporal y el mapa de próximas ocurrencias por día no participan en
cada request: se calculan una sola vez al resolver la configuración de la sesión
y quedan en las instrucciones inmutables.

Fuentes:

- https://developers.openai.com/api/docs/models/gpt-5.6-luna
- https://docs.livekit.io/reference/agents/turn-handling-options/
- https://docs.livekit.io/agents/logic/turns/adaptive-interruption-handling/
- https://docs.livekit.io/deploy/observability/data/
- https://docs.livekit.io/agents/models/stt/deepgram/
