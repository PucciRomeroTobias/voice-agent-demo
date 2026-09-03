import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from agent import (
    INACTIVITY_MESSAGES,
    TURN_HANDLING,
    USER_AWAY_TIMEOUT_SECONDS,
    VoiceDemoAgent,
    complete_scenario_after_confirmation,
    create_end_call_tool,
    create_stt,
    end_call_after_goodbye,
    handle_consecutive_inactivity,
    language_from_code,
    publish_scenario_result,
)
from voice_demo.config import resolve_session_config
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
async def test_completed_scenario_confirms_before_publishing_and_saying_goodbye(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    confirmation = MagicMock()
    confirmation.wait_for_playout = AsyncMock()
    goodbye = AsyncMock()
    monkeypatch.setattr("agent.end_call_after_goodbye", goodbye)
    participant = AsyncMock()
    scenario_session = ScenarioSession(SCENARIOS["clinic"])
    scenario_session.record_tool_use(
        {"appointment_date": "2026-09-10", "appointment_time": "14:30"}
    )
    session = MagicMock()
    session.say.return_value = confirmation
    job = MagicMock()

    await complete_scenario_after_confirmation(
        session, job, participant, scenario_session, "en"
    )

    session.say.assert_called_once_with(
        "All set, your request has been confirmed.",
        allow_interruptions=False,
    )
    confirmation.wait_for_playout.assert_awaited_once()
    participant.publish_data.assert_awaited_once_with(
        json.dumps(scenario_session.result()),
        topic="voice-demo-result",
    )
    goodbye.assert_awaited_once_with(
        session,
        job,
        "Thank you for calling. Goodbye.",
        reason="scenario completed",
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
        allow_interruptions=True,
    )
    speech.wait_for_playout.assert_awaited_once()
    job.shutdown.assert_called_once_with("conversation ended by user")


@pytest.mark.asyncio
async def test_consecutive_inactivity_nudges_twice_and_closes_on_third_turn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    speech = MagicMock()
    speech.wait_for_playout = AsyncMock()
    session = MagicMock()
    session.say.return_value = speech
    job = MagicMock()
    sleep = AsyncMock()
    monkeypatch.setattr("agent.asyncio.sleep", sleep)

    await handle_consecutive_inactivity(session, job, "es")

    assert [call.args[0] for call in session.say.call_args_list] == list(
        INACTIVITY_MESSAGES["es"]
    )
    assert all(
        call.kwargs == {"allow_interruptions": True}
        for call in session.say.call_args_list
    )
    assert speech.wait_for_playout.await_count == 3
    assert sleep.await_count == 2
    sleep.assert_awaited_with(USER_AWAY_TIMEOUT_SECONDS)
    job.shutdown.assert_called_once_with("conversation ended after inactivity")


@pytest.mark.parametrize(
    ("code", "expected"),
    [("es", "es"), ("es-AR", "es"), ("EN-us", "en"), ("pt-BR", None), (None, None)],
)
def test_language_from_code_accepts_supported_bcp47_codes(
    code: object, expected: str | None
) -> None:
    assert language_from_code(code) == expected


def test_voice_llm_uses_bounded_private_generation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    llm = MagicMock()
    constructor = MagicMock(return_value=llm)
    monkeypatch.setattr("agent.openai.responses.LLM", constructor)

    agent = VoiceDemoAgent(resolve_session_config(None, {}), MagicMock())

    constructor.assert_called_once_with(
        model="gpt-5.6-luna",
        reasoning={"effort": "none"},
        max_output_tokens=300,
        store=False,
    )
    assert agent.llm is llm


def test_turn_handling_is_tuned_for_low_latency_and_supported_interruption() -> None:
    assert TURN_HANDLING["endpointing"] == {
        "mode": "dynamic",
        "min_delay": 0.2,
        "max_delay": 1.5,
        "alpha": 0.7,
    }
    assert TURN_HANDLING["interruption"]["mode"] == "adaptive"
    assert TURN_HANDLING["preemptive_generation"] == {
        "enabled": True,
        "preemptive_tts": True,
    }


def test_stt_streams_multilingual_audio_with_word_alignment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LIVEKIT_API_KEY", "test-key")
    monkeypatch.setenv("LIVEKIT_API_SECRET", "test-secret")

    stt = create_stt()

    assert stt._opts.model == "deepgram/nova-3"  # type: ignore[attr-defined]
    assert stt._opts.language == "multi"  # type: ignore[attr-defined]
    assert stt.capabilities.streaming is True
    assert stt.capabilities.interim_results is True
    assert stt.capabilities.aligned_transcript == "word"


@pytest.mark.parametrize(
    ("language", "expected_goodbye"),
    [
        ("es", "Gracias por comunicarte. Hasta luego."),
        ("en", "Thank you for calling. Goodbye."),
    ],
)
@pytest.mark.asyncio
async def test_end_call_uses_the_language_of_the_latest_user_turn(
    monkeypatch: pytest.MonkeyPatch,
    language: str,
    expected_goodbye: str,
) -> None:
    goodbye = AsyncMock()
    monkeypatch.setattr("agent.end_call_after_goodbye", goodbye)
    session = MagicMock()
    job = MagicMock()
    tool = create_end_call_tool(session, job)

    await tool(language=language)
    await asyncio.sleep(0)

    goodbye.assert_awaited_once_with(session, job, expected_goodbye)
