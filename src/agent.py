"""Entrypoint del agente LiveKit de la demo pública."""

import asyncio
import json

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    TurnHandlingOptions,
    cli,
    function_tool,
    inference,
)

from voice_demo.config import AGENT_NAME, SessionConfig, resolve_session_config
from voice_demo.scenarios import ScenarioSession, tools_for

load_dotenv(".env.local")


class VoiceDemoAgent(Agent):
    def __init__(self, config: SessionConfig, end_call_tool: object) -> None:
        self.scenario_session = ScenarioSession(config.scenario)
        super().__init__(
            llm=inference.LLM(model="google/gemma-4-31b-it"),
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
        stt=inference.STT(model="deepgram/nova-3", language=config.language),
        tts=inference.TTS(
            model="inworld/inworld-tts-2",
            voice=config.tts_voice,
            language=config.language,
        ),
        turn_handling=TurnHandlingOptions(
            turn_detection=inference.TurnDetector(),
            interruption={"mode": "adaptive"},
            preemptive_generation={"enabled": True},
        ),
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

    await session.start(agent=agent, room=ctx.room)
    await ctx.connect()
    session.say(config.greeting, allow_interruptions=False)


if __name__ == "__main__":
    cli.run_app(server)
