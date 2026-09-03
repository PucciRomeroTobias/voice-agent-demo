"""Entrypoint del agente LiveKit de la demo pública."""

import asyncio
import json

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    cli,
    function_tool,
    inference,
    metrics,
)
from livekit.plugins import openai

from voice_demo.config import (
    AGENT_NAME,
    TTS_INSTRUCTIONS,
    Language,
    SessionConfig,
    resolve_session_config,
)
from voice_demo.scenarios import ScenarioSession, tools_for

load_dotenv(".env.local")
MAX_SESSION_SECONDS = 2 * 60
USER_AWAY_TIMEOUT_SECONDS = 7
STT_MODEL = "deepgram/nova-3"
STT_LANGUAGE = "multi"
INACTIVITY_MESSAGES: dict[Language, tuple[str, str, str]] = {
    "es": (
        "¿Seguís ahí? Cuando quieras, podemos continuar.",
        "¿Querés que sigamos con esto?",
        "Como no recibí respuesta, voy a finalizar la llamada. Gracias por comunicarte.",
    ),
    "en": (
        "Are you still there? We can continue whenever you're ready.",
        "Would you like to keep going?",
        "Since I haven't heard back, I'll end the call now. Thank you for contacting us.",
    ),
}
TURN_HANDLING = {
    "endpointing": {
        "mode": "dynamic",
        "min_delay": 0.2,
        "max_delay": 1.5,
        "alpha": 0.7,
    },
    "interruption": {
        "enabled": True,
        "mode": "adaptive",
        "min_duration": 0.5,
    },
    "preemptive_generation": {
        "enabled": True,
        "preemptive_tts": True,
    },
}


def create_stt() -> inference.STT:
    """Crea el STT bilingüe streaming provisto por LiveKit Inference."""

    return inference.STT(model=STT_MODEL, language=STT_LANGUAGE)


class VoiceDemoAgent(Agent):
    def __init__(self, config: SessionConfig, end_call_tool: object) -> None:
        self.scenario_session = ScenarioSession(
            config.scenario, local_date=config.local_date
        )
        super().__init__(
            llm=openai.responses.LLM(
                model="gpt-5.6-luna",
                reasoning={"effort": "none"},
                max_output_tokens=300,
                store=False,
            ),
            instructions=config.system_prompt,
            tools=[*tools_for(self.scenario_session), end_call_tool],
        )


server = AgentServer()


async def publish_scenario_result(
    participant: object, scenario_session: ScenarioSession
) -> None:
    """Publica el resultado seguro al terminar una herramienta mock."""

    await participant.publish_data(  # type: ignore[attr-defined]
        json.dumps(scenario_session.result()),
        topic="voice-demo-result",
    )


async def complete_scenario_after_confirmation(
    session: AgentSession,
    ctx: JobContext,
    participant: object,
    scenario_session: ScenarioSession,
    language: Language,
) -> None:
    """Confirma la gestión, entrega el resumen a la UI y se despide en ese orden."""

    confirmation = (
        "Listo, la gestión quedó confirmada."
        if language == "es"
        else "All set, your request has been confirmed."
    )
    goodbye = (
        "Gracias por comunicarte. Hasta luego."
        if language == "es"
        else "Thank you for calling. Goodbye."
    )
    speech = session.say(confirmation, allow_interruptions=False)
    await speech.wait_for_playout()
    await publish_scenario_result(participant, scenario_session)
    await end_call_after_goodbye(
        session,
        ctx,
        goodbye,
        reason="scenario completed",
    )


async def end_call_after_goodbye(
    session: AgentSession,
    ctx: JobContext,
    goodbye: str,
    reason: str = "conversation ended by user",
) -> None:
    """Reproduce la despedida completa antes de cerrar el job de LiveKit."""

    speech = session.say(goodbye, allow_interruptions=True)
    await speech.wait_for_playout()
    ctx.shutdown(reason)


async def end_call_after_limit(
    session: AgentSession, ctx: JobContext, language: str
) -> None:
    """Advierte y termina una sesión pública que alcanzó su duración máxima."""

    await asyncio.sleep(MAX_SESSION_SECONDS)
    goodbye = (
        "Llegamos al tiempo máximo de esta llamada. Gracias por comunicarte."
        if language == "es"
        else "We've reached the time limit for this call. Thank you for contacting us."
    )
    await end_call_after_goodbye(
        session,
        ctx,
        goodbye,
        reason="conversation reached maximum duration",
    )


async def handle_consecutive_inactivity(
    session: AgentSession,
    ctx: JobContext,
    language: Language,
) -> None:
    """Hace dos seguimientos y cierra en el tercer turno sin respuesta."""

    first_nudge, second_nudge, goodbye = INACTIVITY_MESSAGES[language]
    for message in (first_nudge, second_nudge):
        speech = session.say(message, allow_interruptions=True)
        await speech.wait_for_playout()
        await asyncio.sleep(USER_AWAY_TIMEOUT_SECONDS)

    await end_call_after_goodbye(
        session,
        ctx,
        goodbye,
        reason="conversation ended after inactivity",
    )


def language_from_code(value: object) -> Language | None:
    """Reduce un código BCP-47 detectado por STT a un idioma soportado."""

    if not isinstance(value, str):
        return None
    primary = value.lower().split("-", maxsplit=1)[0]
    if primary == "es" or primary == "en":
        return primary
    return None


def create_end_call_tool(
    session: AgentSession,
    ctx: JobContext,
) -> object:
    """Crea la única acción que puede finalizar la llamada a pedido del usuario."""

    @function_tool(
        name="end_call",
        description=(
            "Finaliza la llamada cuando la persona dice que quiere terminar, despedirse "
            "o que no necesita más ayuda. `language` debe ser el idioma de la última "
            "intervención de la persona: `es` o `en`. Reproduce una despedida y corta la sesión."
        ),
    )
    async def end_call(language: Language) -> dict[str, bool]:
        goodbye = (
            "Gracias por comunicarte. Hasta luego."
            if language == "es"
            else "Thank you for calling. Goodbye."
        )
        asyncio.create_task(end_call_after_goodbye(session, ctx, goodbye))
        return {"call_ended": True}

    return end_call


@server.rtc_session(
    agent_name=AGENT_NAME,
)
async def voice_demo(ctx: JobContext) -> None:
    """Inicia una sesión cuyo saludo usa el idioma elegido en metadata."""

    config = resolve_session_config(ctx.job.metadata)
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "language": config.language,
        "scenario": config.scenario.id,
    }

    session = AgentSession(
        stt=create_stt(),
        tts=openai.TTS(
            model="gpt-4o-mini-tts",
            voice=config.tts_voice,
            speed=config.tts_speed,
            instructions=TTS_INSTRUCTIONS,
        ),
        turn_handling=TURN_HANDLING,
        user_away_timeout=USER_AWAY_TIMEOUT_SECONDS,
    )
    agent = VoiceDemoAgent(config, create_end_call_tool(session, ctx))
    active_language: Language = config.language
    idle_task: asyncio.Task[None] | None = None
    completion_task: asyncio.Task[None] | None = None

    @session.on("function_tools_executed")
    def schedule_scenario_result(_: object) -> None:
        """Cierra una gestión completada después de confirmarla en voz."""

        nonlocal completion_task
        if not agent.scenario_session.used_tools:
            return
        if completion_task is not None and not completion_task.done():
            return

        completion_task = asyncio.create_task(
            complete_scenario_after_confirmation(
                session,
                ctx,
                ctx.room.local_participant,
                agent.scenario_session,
                active_language,
            )
        )

    @session.on("metrics_collected")
    def log_pipeline_metrics(event: object) -> None:
        """Registra latencias técnicas por etapa, sin audio ni transcripciones."""

        metric = getattr(event, "metrics", None)
        if metric is not None:
            metrics.log_metrics(metric)

    @session.on("user_state_changed")
    def follow_up_when_user_is_away(event: object) -> None:
        """Inicia o cancela el seguimiento de silencios consecutivos."""

        nonlocal idle_task

        if getattr(event, "new_state", None) == "away":
            if idle_task is None or idle_task.done():
                idle_task = asyncio.create_task(
                    handle_consecutive_inactivity(session, ctx, active_language)
                )
        elif idle_task is not None:
            idle_task.cancel()
            idle_task = None

    @session.on("user_input_transcribed")
    def remember_latest_language(event: object) -> None:
        """Mantiene los avisos de inactividad en el idioma detectado más reciente."""

        nonlocal active_language
        if not getattr(event, "is_final", False):
            return
        detected = language_from_code(getattr(event, "language", None))
        if detected is not None:
            active_language = detected

    await session.start(agent=agent, room=ctx.room)
    await ctx.connect()
    session.say(config.greeting, allow_interruptions=False)
    asyncio.create_task(end_call_after_limit(session, ctx, config.language))


if __name__ == "__main__":
    cli.run_app(server)
