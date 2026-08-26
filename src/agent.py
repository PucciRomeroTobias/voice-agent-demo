"""Entrypoint del agente LiveKit de la demo pública."""

import json

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    TurnHandlingOptions,
    cli,
    inference,
)

from voice_demo.config import AGENT_NAME, SessionConfig, resolve_session_config
from voice_demo.scenarios import ScenarioSession, tools_for

load_dotenv(".env.local")


class VoiceDemoAgent(Agent):
    def __init__(self, config: SessionConfig) -> None:
        self.scenario_session = ScenarioSession(config.scenario)
        super().__init__(
            llm=inference.LLM(model="google/gemma-4-31b-it"),
            instructions=config.system_prompt,
            tools=tools_for(self.scenario_session),
        )


server = AgentServer()


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
    agent = VoiceDemoAgent(config)

    @session.on("function_tools_executed")
    def publish_scenario_result(_: object) -> None:
        """Comparte sólo el resumen seguro que consumirá la UI al finalizar."""

        ctx.room.local_participant.publish_data(
            json.dumps(agent.scenario_session.result()),
            topic="voice-demo-result",
        )

    await session.start(agent=agent, room=ctx.room)
    await ctx.connect()
    await session.generate_reply(instructions=config.greeting)


if __name__ == "__main__":
    cli.run_app(server)
