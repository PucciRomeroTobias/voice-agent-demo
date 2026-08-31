# Inactividad y referencias temporales

Investigación realizada el 2026-08-30 para PRO-24.

## Inactividad en LiveKit

`AgentSession.user_away_timeout` cambia el estado del usuario a `away` después
del período configurado de silencio mutuo entre la persona y el agente. La demo
oficial `survey` de LiveKit escucha `user_state_changed`, inicia una tarea de
seguimiento mientras el estado es `away` y la cancela cuando la persona vuelve.

La implementación adopta ese patrón con un timeout de 7 segundos. Usa mensajes
deterministas para poder garantizar dos seguimientos y un cierre en el tercer
turno, sin depender de que el LLM genere o cuente correctamente los avisos.

Fuentes:

- https://github.com/livekit/agents/blob/main/examples/survey/agent.py
- https://github.com/livekit/agents/blob/main/livekit-agents/livekit/agents/voice/agent_session.py

## Fecha, hora y expresiones relativas

El runtime inyecta al final del prompt un reloj de sesión con fecha, hora y la
zona IANA `America/Argentina/Buenos_Aires`. OpenAI recomienda prompts concisos,
sin repetir reglas, y conservar contexto de dominio y restricciones relevantes
para GPT-5.6. El bloque temporal es dinámico y se agrega después de la base
estable del prompt.

Para evitar delegar aritmética de calendario al modelo, el runtime calcula y
enumera la próxima ocurrencia futura de cada día. Así, tanto el domingo
2026-08-30 como el lunes 2026-08-31 queda explícito que el próximo miércoles es
2026-09-02, incluso si “next week” y “Wednesday” llegan en turnos separados. Una
fecha absoluta o una semana identificada explícitamente prevalecen. Las tools de
agenda validan además fecha ISO y hora `HH:MM`, de modo que una expresión
relativa sin resolver no puede quedar registrada como argumento. El reloj y el
mapa se fijan al abrir la llamada porque la sesión dura como máximo dos minutos.

Fuente:

- https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6
