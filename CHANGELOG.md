# Changelog

Todos los cambios relevantes de este proyecto se documentan aquí.

El formato sigue [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) y el
versionado seguirá [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Las voces se seleccionan por escenario e idioma; las sesiones en English usan
  una voz inglesa y los prompts piden una cadencia breve que cede el turno al
  detectar que la persona empieza a hablar.
- La UI presenta estados de conexión, escucha, razonamiento y habla con
  etiquetas legibles, y distingue cada intervención del agente y de la persona
  en la transcripción.
- Cada escenario reúne los datos necesarios antes de invocar su mock: fecha y
  hora para Clínica, necesidad más fecha y hora para SaaS, y área, impacto y
  descripción para Soporte. Ningún mock crea recursos reales.
- Los saludos iniciales presentan el rol del agente y hacen la primera pregunta
  útil, sin imponer horarios ni datos de prueba.

### Fixed

- El resultado de una herramienta mockeada vuelve a llegar a la UI al terminar
  su ejecución.
- La web ahora renderiza el audio remoto de LiveKit y ofrece activar audio si el
  navegador bloquea la reproducción automática.
- El agente se despide y termina la llamada cuando la persona expresa que ya no
  necesita ayuda.

### Added

- Endpoint server-side para emitir tokens breves de LiveKit con rooms únicas,
  validación de idioma/escenario y dispatch explícito del agente.
- Página responsive de la demo con Session + TokenSource, transcripciones,
  estados de llamada y resumen de negocio recibido por datos de LiveKit.
- Registro de escenarios Clínica, SaaS B2B y Soporte con prompts, voces,
  datos de prueba, mocks deterministas y resultados estructurados por sesión.
- Runtime inicial de LiveKit Agents en Python.
- Configuración inmutable de idioma por sesión para Español e English.
- Pipeline STT → LLM → TTS con LiveKit Inference.
- Pruebas de configuración y guía de contribución para agentes.
