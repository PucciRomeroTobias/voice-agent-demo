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
)
from livekit.plugins import openai

from voice_demo.config import AGENT_NAME, SessionConfig, resolve_session_config
from voice_demo.scenarios import ScenarioSession, tools_for

load_dotenv(".env.local")
MAX_SESSION_SECONDS = 2 * 60
MAX_IDLE_SECONDS = 30


class VoiceDemoAgent(Agent):
    def __init__(self, config: SessionConfig, end_call_tool: object) -> None:
        self.scenario_session = ScenarioSession(config.scenario)
        super().__init__(
            llm=openai.responses.LLM(
                model="gpt-5.6-luna",
                reasoning={"effort": "low"},
                max_output_tokens=300,
            ),
            instructions=config.system_prompt,
            tools=[*tools_for(self.scenario_session), end_call_tool],
        )


server = AgentServer()


async def publish_scenario_result(participant: object, scenario_session: ScenarioSession) -> None:
    """Publica el resultado seguro al terminar una herramienta mock."""

    await participant.publish_data(  # type: ignore[attr-defined]
        json.dumps(scenario_session.result()),
        topic="voice-demo-result",
    )


async def end_call_after_goodbye(
    session: AgentSession,
    ctx: JobContext,
    goodbye: str,
) -> None:
    """Reproduce la despedida completa antes de cerrar el job de LiveKit."""

    speech = session.say(goodbye, allow_interruptions=False)
    await speech.wait_for_playout()
    ctx.shutdown("conversation ended by user")


async def end_call_after_limit(session: AgentSession, ctx: JobContext, language: str) -> None:
    """Advierte y termina una sesión pública que alcanzó su duración máxima."""

    await asyncio.sleep(MAX_SESSION_SECONDS)
    goodbye = (
        "Llegamos al máximo de dos minutos de esta demo. Gracias por probarla."
        if language == "es"
        else "This demo has reached its two-minute limit. Thank you for trying it."
    )
    await end_call_after_goodbye(session, ctx, goodbye)


async def end_call_after_inactivity(
    session: AgentSession,
    ctx: JobContext,
    language: str,
) -> None:
    """Cierra una sesión pública cuando la persona deja de interactuar."""

    goodbye = (
        "Como no detecté actividad, voy a cerrar esta demo. Gracias por probarla."
        if language == "es"
        else "I did not detect activity, so I will close this demo. Thank you for trying it."
    )
    await end_call_after_goodbye(session, ctx, goodbye)


def create_end_call_tool(
    session: AgentSession,
    ctx: JobContext,
    goodbye: str,
) -> object:
    """Crea la única acción que puede finalizar la llamada a pedido del usuario."""

    @function_tool(
        name="end_call",
        description=(
            "Finaliza la llamada cuando la persona dice que quiere terminar, despedirse "
            "o que no necesita más ayuda. Reproduce una despedida y corta la sesión."
        ),
    )
    async def end_call() -> dict[str, bool]:
        asyncio.create_task(end_call_after_goodbye(session, ctx, goodbye))
        return {"call_ended": True}

    return end_call


@server.rtc_session(agent_name=AGENT_NAME)
async def voice_demo(ctx: JobContext) -> None:
    """Inicia una sesión con el idioma ya fijado por su metadata."""

    config = resolve_session_config(ctx.job.metadata)
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "language": config.language,
        "scenario": config.scenario.id,
    }

    session = AgentSession(
        stt=openai.STT(
            model="gpt-transcribe",
            language=config.language,
            prompt=(
                "La conversación puede incluir español rioplatense de Argentina, "
                "nombres propios y términos de Voice AI, LiveKit y LLM."
                if config.language == "es"
                else "The conversation may include Voice AI, LiveKit, and LLM terminology."
            ),
        ),
        tts=openai.TTS(
            model="gpt-4o-mini-tts",
            voice=config.tts_voice,
            instructions=(
                "Hablá español rioplatense argentino natural, cálido y profesional. "
                "Usá voseo cuando corresponda, una dicción clara y una cadencia conversacional."
                if config.language == "es"
                else "Speak natural, warm, professional English with clear conversational pacing."
            ),
        ),
        user_away_timeout=MAX_IDLE_SECONDS,
    )
    goodbye = (
        "Gracias por comunicarte. Hasta luego."
        if config.language == "es"
        else "Thank you for calling. Goodbye."
    )
    agent = VoiceDemoAgent(config, create_end_call_tool(session, ctx, goodbye))

    @session.on("function_tools_executed")
    def schedule_scenario_result(_: object) -> None:
        """Comparte sólo el resumen seguro que consumirá la UI al finalizar."""

        asyncio.create_task(
            publish_scenario_result(
                ctx.room.local_participant,
                agent.scenario_session,
            )
        )

    @session.on("user_state_changed")
    def close_when_user_is_away(event: object) -> None:
        """Termina la room cuando LiveKit confirma inactividad sostenida."""

        if getattr(event, "new_state", None) == "away":
            asyncio.create_task(end_call_after_inactivity(session, ctx, config.language))

    await session.start(agent=agent, room=ctx.room)
    await ctx.connect()
    session.say(config.greeting, allow_interruptions=False)
    asyncio.create_task(end_call_after_limit(session, ctx, config.language))


if __name__ == "__main__":
    cli.run_app(server)
