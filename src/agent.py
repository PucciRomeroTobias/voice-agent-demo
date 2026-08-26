"""Entrypoint del agente LiveKit de la demo pública."""

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

load_dotenv(".env.local")


class VoiceDemoAgent(Agent):
    def __init__(self, config: SessionConfig) -> None:
        super().__init__(
            llm=inference.LLM(model="google/gemma-4-31b-it"),
            instructions=config.system_prompt,
        )


server = AgentServer()


@server.rtc_session(agent_name=AGENT_NAME)
async def voice_demo(ctx: JobContext) -> None:
    """Inicia una sesión con el idioma ya fijado por su metadata."""

    config = resolve_session_config(ctx.job.metadata)
    ctx.log_context_fields = {
        "room": ctx.room.name,
        "language": config.language,
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

    await session.start(agent=VoiceDemoAgent(config), room=ctx.room)
    await ctx.connect()
    await session.generate_reply(instructions=config.greeting)


if __name__ == "__main__":
    cli.run_app(server)
