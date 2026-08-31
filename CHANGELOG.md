# Changelog

Todos los cambios relevantes de este proyecto se documentan aquí.

El formato sigue [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) y el
versionado seguirá [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed

- La web standalone, su endpoint de tokens, scripts y dependencias de Node. La
  UI de producto vive fuera de este runtime.
- La configuración versionada del agente de una cuenta específica de LiveKit.

### Changed

- `gpt-5.6-luna` usa explícitamente reasoning `none`. El endpointing pasa a modo
  dinámico entre 0,2 y 1,5 segundos y habilita TTS preemptivo para reducir la
  latencia percibida.
- El STT pasa de `gpt-transcribe` no-streaming a Deepgram Nova-3 multilingual
  mediante LiveKit Inference, con resultados intermedios y alineación por
  palabra. Las interrupciones vuelven al modo adaptativo compatible. Se agregan
  métricas técnicas por etapa.
- La inactividad genera seguimientos a los 7 y 14 segundos de silencio mutuo y
  cierra en el tercer turno, cerca de los 21 segundos; si la persona responde,
  la secuencia se cancela y reinicia. Los avisos siguen el último idioma detectado.
- Cada sesión inyecta fecha, hora, zona `America/Argentina/Buenos_Aires` y un
  mapa ya calculado con la próxima ocurrencia futura de cada día. El agente
  resuelve fechas relativas contra ese mapa y normaliza los argumentos de
  herramientas a `YYYY-MM-DD`. Esto evita que “Wednesday next week” salte del
  2 al 9 de septiembre al cruzar de domingo a lunes. Clínica y SaaS comunican
  amplia disponibilidad esta semana y la próxima cuando la persona pregunta.
- Los tres agentes completan el flujo sin decir “simulación” o “ficticio”. El
  resultado de la tool que consume el LLM confirma la gestión, mientras el resumen
  técnico publicado a la UI sigue aclarando que no hubo persistencia real.
- El TTS usa velocidad `1.40` en ambos idiomas y una entrega conversacional más
  ágil. LiveKit permite interrupciones durante toda la conversación salvo el
  saludo inicial, incluido el cierre de llamada.
- El idioma de metadata define sólo el saludo inicial. Deepgram Nova-3 usa modo
  multilingüe para reconocer code-switching, y el agente responde en el idioma
  principal de la última intervención, incluido el cierre manual.
- Las voces de TTS se distinguen por escenario en ambos idiomas: `alloy` para
  Clínica, `echo` para SaaS B2B y `nova` para Soporte.
- Los prompts ahora separan identidad, reglas de voz, flujo, uso seguro de
  herramientas y guardrails por escenario. Clínica evita consejo médico y
  deriva urgencias; SaaS evita capturar datos comerciales; Soporte evita pedir
  secretos o acceso. Los saludos suenan como una atención humana y abierta; el
  alcance se explica recién luego de la primera intervención. Los pedidos fuera
  del objetivo se redirigen sin cambiar de rol.
- Las voces se seleccionan por escenario e idioma; las sesiones en English usan
  una voz inglesa y los prompts piden una cadencia breve que cede el turno al
  detectar que la persona empieza a hablar.
- Cada escenario reúne los datos necesarios antes de invocar su mock: fecha y
  hora para Clínica, necesidad más fecha y hora para SaaS, y área, impacto y
  descripción para Soporte. Cada mock admite `extra_notes` opcionales y no
  personales ya compartidos para confirmar el resultado en contexto. Ningún
  mock crea recursos reales.
- Los saludos iniciales presentan el rol del agente y hacen la primera pregunta
  útil, sin imponer horarios ni datos de prueba.

### Added

- Export privado al finalizar cada sesión con transcript, tool calls, eventos y
  métricas por turno, autenticado contra el Worker Cloudflare y sin audio. Los
  artefactos se recuperan por session ID y expiran a los 30 días.
- Registro de escenarios Clínica, SaaS B2B y Soporte con prompts, voces,
  datos de prueba, mocks deterministas y resultados estructurados por sesión.
- Runtime inicial de LiveKit Agents en Python.
- Configuración bilingüe con idioma inicial por sesión y adaptación por turno
  entre Español e English.
- Pipeline STT → LLM → TTS con LiveKit Inference.
- Pruebas de configuración y guía de contribución para agentes.
