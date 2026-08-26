# Voice Agent Demo — guía para agentes

## Objetivo del repositorio

Este repositorio contiene la demo pública de un agente de voz bilingüe. Debe
mostrar una conversación fluida en Español o English con LiveKit Cloud, sin
persistencia ni datos personales.

El alcance de producto y las decisiones canónicas se gestionan en Linear. La
implementación local no debe inventar escenarios, integraciones o requisitos
fuera de los tickets activos.

## Principios de código

- KISS: preferir la solución más pequeña y legible que satisfaga el ticket.
- YAGNI: no introducir extensiones, capas o configuraciones para futuros
  escenarios hasta que un ticket las requiera.
- DRY: eliminar duplicación sólo cuando comparta una responsabilidad real; no
  crear abstracciones genéricas por coincidencias superficiales.
- Mantener módulos con una responsabilidad clara y nombres del dominio de la
  demo. Favorecer funciones puras para configuración y validación.

## Mapa del código

- `src/agent.py`: único entrypoint de LiveKit; conserva este path para la CLI y
  el futuro despliegue.
- `src/voice_demo/config.py`: configuración no secreta e inmutable por sesión.
- `tests/`: pruebas rápidas, deterministas y sin red.
- `docs/architecture.md`: límites del runtime y contrato de configuración.
- `CHANGELOG.md`: registro de cambios orientado a usuarios del repositorio.

## Comandos obligatorios antes de entregar un cambio

```sh
uv sync
uv run pytest
uv run ruff check src tests
```

Para comprobar voz real, sólo cuando exista `.env.local` con credenciales
válidas de LiveKit Cloud:

```sh
uv run python src/agent.py console
```

No simules esa verificación ni agregues credenciales de prueba a archivos.

## Reglas de implementación

- Mantener `AGENT_NAME = "voice-demo"` estable. Cambiarlo rompe el dispatch.
- El idioma se elige al comienzo de la sesión y no cambia durante ella.
- Separar prompts, voces y configuración no secreta del entrypoint. Evitar
  abstracciones preventivas: los escenarios mockeados pertenecen a su ticket.
- No registrar ni persistir audio, transcripciones, PII, tokens o secretos.
- Mantener `.env.local` local y actualizar `.env.example` sólo con nombres de
  variables, nunca valores sensibles.
- Escribir pruebas para toda modificación de selección de idioma, metadata o
  configuración de sesión.

## Documentación al cerrar un issue

Linear es el registro canónico del issue: al cerrarlo, registrar ahí el
resultado, las verificaciones y las decisiones tomadas. No crear un documento
por ticket ni copiar su narrativa al repositorio.

Actualizar sólo el artefacto durable que corresponda:

| Si cambió… | Actualizar… |
| --- | --- |
| Un contrato, límite, componente o flujo entre cliente, endpoint y agente | `docs/architecture.md` |
| Un hallazgo de investigación que seguirá guiando decisiones | `docs/research/<tema>.md`, con fuentes primarias y su aplicación concreta |
| El comportamiento, capacidad o forma de usar el repositorio | `CHANGELOG.md` bajo `Unreleased` |
| La instalación o los comandos que necesita una persona | `README.md` |

Si no aplica ninguna fila, alcanza con Linear. La documentación debe decir el
estado actual del sistema, no relatar el proceso de implementación.

## Cómo hacer cambios seguros

1. Leé el ticket activo y estos archivos antes de editar.
2. Hacé el cambio más chico que cumpla el criterio de aceptación.
3. Ejecutá las verificaciones aplicables e informá exactamente cuáles no fueron
   posibles y por qué.
4. No hagas `git commit`, `git push` ni deploy sin autorización explícita.
