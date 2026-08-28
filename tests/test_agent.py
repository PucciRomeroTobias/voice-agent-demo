import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from agent import (
    end_call_after_goodbye,
    end_call_after_inactivity,
    publish_scenario_result,
)
from voice_demo.scenarios import SCENARIOS, ScenarioSession


@pytest.mark.asyncio
async def test_publish_scenario_result_sends_the_session_summary() -> None:
    participant = AsyncMock()
    scenario_session = ScenarioSession(SCENARIOS["clinic"])
    scenario_session.record_tool_use(
        {"appointment_date": "2026-09-10", "appointment_time": "14:30"}
    )

    await publish_scenario_result(participant, scenario_session)

    participant.publish_data.assert_awaited_once_with(
        json.dumps(scenario_session.result()),
        topic="voice-demo-result",
    )


@pytest.mark.asyncio
async def test_end_call_waits_for_the_goodbye_before_shutting_down() -> None:
    speech = MagicMock()
    speech.wait_for_playout = AsyncMock()
    session = MagicMock()
    session.say.return_value = speech
    job = MagicMock()

    await end_call_after_goodbye(session, job, "Gracias por comunicarte. Hasta luego.")

    session.say.assert_called_once_with(
        "Gracias por comunicarte. Hasta luego.",
        allow_interruptions=False,
    )
    speech.wait_for_playout.assert_awaited_once()
    job.shutdown.assert_called_once_with("conversation ended by user")


@pytest.mark.asyncio
async def test_end_call_after_inactivity_closes_the_session() -> None:
    speech = MagicMock()
    speech.wait_for_playout = AsyncMock()
    session = MagicMock()
    session.say.return_value = speech
    job = MagicMock()

    await end_call_after_inactivity(session, job, "es")

    session.say.assert_called_once_with(
        "Como no detecté actividad, voy a cerrar esta demo. Gracias por probarla.",
        allow_interruptions=False,
    )
    job.shutdown.assert_called_once_with("conversation ended by user")
