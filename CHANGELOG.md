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

- Las voces se seleccionan por escenario e idioma; las sesiones en English usan
  una voz inglesa y los prompts piden una cadencia breve que cede el turno al
  detectar que la persona empieza a hablar.
- Cada escenario reúne los datos necesarios antes de invocar su mock: fecha y
  hora para Clínica, necesidad más fecha y hora para SaaS, y área, impacto y
  descripción para Soporte. Ningún mock crea recursos reales.
- Los saludos iniciales presentan el rol del agente y hacen la primera pregunta
  útil, sin imponer horarios ni datos de prueba.

### Added

- Registro de escenarios Clínica, SaaS B2B y Soporte con prompts, voces,
  datos de prueba, mocks deterministas y resultados estructurados por sesión.
- Runtime inicial de LiveKit Agents en Python.
- Configuración inmutable de idioma por sesión para Español e English.
- Pipeline STT → LLM → TTS con LiveKit Inference.
- Pruebas de configuración y guía de contribución para agentes.
