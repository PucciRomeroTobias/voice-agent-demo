# Changelog

Todos los cambios relevantes de este proyecto se documentan aquí.

El formato sigue [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) y el
versionado seguirá [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
