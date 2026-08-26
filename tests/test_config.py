from dataclasses import FrozenInstanceError

import pytest

from voice_demo.config import AGENT_NAME, resolve_session_config


def test_defaults_to_spanish_for_local_console() -> None:
    config = resolve_session_config(None, {})

    assert config.language == "es"
    assert config.tts_voice == "Diego"


def test_english_metadata_wins_over_local_default() -> None:
    config = resolve_session_config('{"language":"en"}', {"VOICE_DEMO_LANGUAGE": "es"})

    assert config.language == "en"
    assert config.tts_voice == "Ashley"


def test_invalid_input_cannot_select_an_unsupported_language() -> None:
    config = resolve_session_config('{"language":"pt"}', {"VOICE_DEMO_LANGUAGE": "pt"})

    assert config.language == "es"


def test_session_configuration_is_immutable_after_start() -> None:
    config = resolve_session_config('{"language":"en"}', {})

    with pytest.raises(FrozenInstanceError):
        config.language = "es"  # type: ignore[misc]


def test_dispatch_name_is_stable() -> None:
    assert AGENT_NAME == "voice-demo"
