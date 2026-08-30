import json
from typing import Self
from unittest.mock import MagicMock

import pytest

from voice_demo.observability import (
    build_session_artifact,
    persist_session_observability,
    upload_session_artifact,
)


def session_report() -> MagicMock:
    report = MagicMock()
    report.room_id = "RM_test123"
    report.job_id = "AJ_test123"
    report.room = "voice-demo-test"
    report.started_at = 1_000.0
    report.timestamp = 1_012.5
    report.duration = None
    report.to_dict.return_value = {
        "room_id": "RM_test123",
        "job_id": "AJ_test123",
        "audio_recording_path": "/tmp/session.ogg",
        "audio_recording_started_at": 999.0,
        "events": [{"type": "user_input_transcribed", "transcript": "Necesito un turno."}],
        "chat_history": {
            "items": [
                {
                    "role": "user",
                    "content": ["Necesito un turno."],
                    "metrics": {"transcription_delay": 0.2, "end_of_turn_delay": 0.4},
                },
                {
                    "role": "assistant",
                    "content": ["¿Qué día preferís?"],
                    "metrics": {"llm_node_ttft": 0.3, "tts_node_ttfb": 0.1},
                },
            ]
        },
    }
    return report


def test_artifact_keeps_transcript_and_metrics_but_removes_audio() -> None:
    artifact = build_session_artifact(
        session_report(),
        '{"language":"es","scenario":"clinic"}',
    )

    assert artifact["session_id"] == "RM_test123"
    assert artifact["duration"] == 12.5
    assert artifact["language"] == "es"
    assert artifact["scenario"] == "clinic"
    assert artifact["report"]["chat_history"]["items"][0]["content"] == [
        "Necesito un turno."
    ]
    assert artifact["report"]["chat_history"]["items"][1]["metrics"][
        "llm_node_ttft"
    ] == 0.3
    assert "audio_recording_path" not in artifact["report"]
    assert "audio_recording_started_at" not in artifact["report"]


@pytest.mark.asyncio
async def test_upload_sends_utf8_json_with_bearer_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class Response:
        status = 204

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *_: object) -> None:
            return None

    def urlopen(request: object, timeout: int) -> Response:
        captured["request"] = request
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setattr("voice_demo.observability.urllib.request.urlopen", urlopen)
    artifact = build_session_artifact(session_report(), None)

    await upload_session_artifact(artifact, "https://example.com/private", "secret")

    request = captured["request"]
    assert request.get_header("Authorization") == "Bearer secret"  # type: ignore[union-attr]
    assert json.loads(request.data)["session_id"] == "RM_test123"  # type: ignore[union-attr]
    assert captured["timeout"] == 10


@pytest.mark.asyncio
async def test_session_end_builds_and_uploads_the_report(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    report = session_report()
    context = MagicMock()
    context.make_session_report.return_value = report
    context.job.metadata = '{"language":"en","scenario":"support"}'
    upload = MagicMock()

    async def capture_upload(artifact: dict[str, object], url: str, token: str) -> None:
        upload(artifact, url, token)

    monkeypatch.setenv("VOICE_OBSERVABILITY_URL", "https://example.com/private")
    monkeypatch.setenv("VOICE_OBSERVABILITY_TOKEN", "secret")
    monkeypatch.setattr("voice_demo.observability.upload_session_artifact", capture_upload)

    await persist_session_observability(context)

    context.make_session_report.assert_called_once_with()
    artifact, url, token = upload.call_args.args
    assert artifact["session_id"] == "RM_test123"
    assert artifact["language"] == "en"
    assert artifact["scenario"] == "support"
    assert url == "https://example.com/private"
    assert token == "secret"
