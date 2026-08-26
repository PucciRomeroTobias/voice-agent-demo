# Repositorio apto para agentes de código

Fecha: 2026-08-26

## Qué significa

"Agent-ready" no es una certificación ni requiere una carpeta especial. Para
este proyecto significa que una persona o un agente puede entender el alcance,
preparar el entorno, ejecutar los controles de calidad y hacer un cambio seguro
sin depender de conocimiento oral o de instrucciones repetidas.

La base portátil es `AGENTS.md`: un archivo Markdown para instrucciones de
agentes. La iniciativa AGENTS.md lo plantea como complemento del `README` para
incluir los comandos, pruebas, convenciones y límites que necesita un agente;
no tiene campos obligatorios. [AGENTS.md](https://agents.md/)

## Prácticas respaldadas por fuentes primarias

1. Mantener `AGENTS.md` breve y accionable. Debe funcionar como mapa: propósito
   del repo, comandos exactos de instalación/lint/test/ejecución, reglas de
   seguridad y límites de cambio. El conocimiento profundo y durable va en
   `docs/` versionado. OpenAI advierte que un `AGENTS.md` enciclopédico consume
   contexto y se desactualiza; recomienda un índice corto y documentación
   estructurada como sistema de registro. [Harness engineering — OpenAI](https://openai.com/index/harness-engineering/)

2. Aplicar las instrucciones por cercanía sólo cuando cambie el contexto.
   Las reglas generales viven en el `AGENTS.md` raíz; una carpeta con reglas
   realmente diferentes puede tener su propio `AGENTS.md`. Codex agrega los
   archivos desde la raíz hacia el directorio actual y las instrucciones más
   específicas se aplican después. [Unrolling the Codex agent loop — OpenAI](https://openai.com/index/unrolling-the-codex-agent-loop/)

3. Hacer verificable lo importante. Los comandos documentados deben poder
   ejecutarse sin interacción y los límites arquitectónicos o de seguridad que
   importen deben imponerse mediante tests, lint o CI, con errores que indiquen
   cómo corregirlos. [Harness engineering — OpenAI](https://openai.com/index/harness-engineering/)

4. Separar la guía humana de la guía operativa. El `README` explica qué es el
   proyecto y cómo empezar; `AGENTS.md` añade la información operativa para
   agentes, como convenciones, organización y comandos de prueba. [Introducing
   Codex — OpenAI](https://openai.com/index/introducing-codex/)

5. Priorizar compatibilidad antes que duplicación. GitHub Copilot cloud agent,
   CLI y code review reconocen `AGENTS.md`. GitHub también permite
   `.github/copilot-instructions.md` y reglas por ruta en
   `.github/instructions/**/*.instructions.md`; se justifican sólo si hace
   falta una regla específica de Copilot o de un subconjunto de archivos.
   [Soporte de instrucciones personalizadas — GitHub](https://docs.github.com/en/copilot/reference/custom-instructions-support)

6. Usar instrucciones universales para normas universales y recursos bajo
   demanda para tareas especializadas. GitHub recomienda custom instructions
   para reglas simples que aplican a casi todo el trabajo, y skills para
   conocimiento más detallado que sólo corresponde cargar cuando es relevante.
   [Adding agent skills for GitHub Copilot — GitHub](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)

## Aplicación mínima para `voice-agent`

- Un `AGENTS.md` en la raíz de `voice-agent` con alcance, comandos de setup,
  lint, tests, ejecución local y reglas explícitas: no commitear secretos; no
  modificar las decisiones de escenario/idioma sin actualizar la documentación
  pertinente; validar antes de declarar terminado.
- Un `README.md` dirigido a personas: demo, prerequisitos, configuración desde
  `.env.example`, cómo correrla y cómo contribuir.
- `docs/` para decisiones de arquitectura, operación y esta investigación; no
  repetir esas explicaciones largas en `AGENTS.md`.
- Scripts reproducibles definidos en `pyproject.toml` y un CI que ejecute los
  mismos controles que se piden localmente.
- `.gitignore` y archivos de ejemplo para que credenciales y archivos locales
  no ingresen al historial.
- Un `CHANGELOG.md` mantenido en cada cambio de producto relevante. La
  convención concreta se definirá en el repositorio; no se infiere de las
  fuentes anteriores.

## Límites deliberados

No se crearán skills, agentes a medida, instrucciones de Copilot duplicadas ni
automatizaciones de despliegue hasta que una necesidad concreta lo justifique.
Para este MVP, suman superficie de mantenimiento sin reemplazar los comandos,
tests y documentación claros.
