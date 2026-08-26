from dataclasses import FrozenInstanceError

import pytest

from voice_demo.config import AGENT_NAME, resolve_session_config
from voice_demo.scenarios import ScenarioSession, tools_for


def test_defaults_to_spanish_for_local_console() -> None:
    config = resolve_session_config(None, {})

    assert config.language == "es"
    assert config.tts_voice == "Diego"
    assert config.scenario.id == "clinic"


def test_english_metadata_wins_over_local_default() -> None:
    config = resolve_session_config('{"language":"en"}', {"VOICE_DEMO_LANGUAGE": "es"})

    assert config.language == "en"
    assert config.scenario.id == "clinic"


def test_invalid_input_cannot_select_an_unsupported_language() -> None:
    config = resolve_session_config('{"language":"pt"}', {"VOICE_DEMO_LANGUAGE": "pt"})

    assert config.language == "es"


def test_session_configuration_is_immutable_after_start() -> None:
    config = resolve_session_config('{"language":"en"}', {})

    with pytest.raises(FrozenInstanceError):
        config.language = "es"  # type: ignore[misc]


def test_dispatch_name_is_stable() -> None:
    assert AGENT_NAME == "voice-demo"


def test_metadata_selects_an_allowed_scenario_with_its_own_voice() -> None:
    config = resolve_session_config('{"language":"en", "scenario":"support"}', {})

    assert config.scenario.id == "support"
    assert config.tts_voice == "Olivia"
    assert "first-line support" in config.system_prompt


def test_invalid_scenario_falls_back_to_the_allowed_default() -> None:
    config = resolve_session_config('{"scenario":"technical"}', {})

    assert config.scenario.id == "clinic"


def test_metadata_scenario_wins_over_local_console_default() -> None:
    config = resolve_session_config(
        '{"scenario":"support"}',
        {"VOICE_DEMO_SCENARIO": "saas_b2b"},
    )

    assert config.scenario.id == "support"


@pytest.mark.asyncio
async def test_each_scenario_exposes_only_its_authorized_mock_tool() -> None:
    expected_tools = {
        "clinic": "reserve_appointment",
        "saas_b2b": "create_qualified_lead",
        "support": "escalate_support_case",
    }

    for scenario_id, tool_name in expected_tools.items():
        config = resolve_session_config(f'{{"scenario":"{scenario_id}"}}', {})
        session = ScenarioSession(config.scenario)
        tools = tools_for(session)

        assert [tool.info.name for tool in tools] == [tool_name]
        result = await tools[0]()
        assert result == {
            "scenario": scenario_id,
            "tools_used": [tool_name],
            "outcome": config.scenario.outcome,
        }


def test_mock_state_does_not_cross_sessions() -> None:
    config = resolve_session_config('{"scenario":"saas_b2b"}', {})
    first_session = ScenarioSession(config.scenario)
    second_session = ScenarioSession(config.scenario)

    first_session.record_tool_use()

    assert first_session.result()["tools_used"] == ["create_qualified_lead"]
    assert second_session.result()["tools_used"] == []
