# STT bilingüe y cambio de idioma

## Decisión

La metadata `language` define sólo el saludo inicial. Cada sesión usa Deepgram
Nova-3 mediante LiveKit Inference con `language="multi"`. El modelo detecta el
idioma por segmento dentro del stream; el prompt responde en el idioma principal
del último turno y cambia con la persona.

## Evidencia

- La documentación de LiveKit declara que Nova-3 soporta transcripción
  multilingüe y detección automática del idioma de cada segmento:
  <https://docs.livekit.io/agents/models/stt/deepgram/#multilingual>.
- La versión instalada de LiveKit Agents declara para
  `deepgram/nova-3:multi` capacidades streaming, resultados intermedios y
  alineación de transcript por palabra.

## Límite

La detección automática no garantiza una clasificación perfecta en audio breve,
ruidoso o fuertemente mezclado. La aceptación requiere probar en LiveKit Agent
Console cambios completos de turno y frases con code-switching en ambas
direcciones.
