"""Persistencia privada de conversaciones y métricas de sesiones."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import urllib.error
import urllib.request
from collections.abc import Mapping
from typing import Any

from livekit.agents import JobContext
from livekit.agents.voice.report import SessionReport

from voice_demo.config import AGENT_NAME, resolve_session_config

logger = logging.getLogger(__name__)

OBSERVABILITY_URL_ENV = "VOICE_OBSERVABILITY_URL"
OBSERVABILITY_TOKEN_ENV = "VOICE_OBSERVABILITY_TOKEN"
OBSERVABILITY_SCHEMA_VERSION = 1
UPLOAD_TIMEOUT_SECONDS = 10


def build_session_artifact(
    report: SessionReport,
    metadata: str | None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Construye el artefacto completo sin incluir referencias de audio."""

    config = resolve_session_config(metadata, env or {})
    report_data = report.to_dict()
    report_data.pop("audio_recording_path", None)
    report_data.pop("audio_recording_started_at", None)

    duration = report.duration
    if duration is None and report.started_at is not None:
        duration = max(0.0, report.timestamp - report.started_at)

    return {
        "schema_version": OBSERVABILITY_SCHEMA_VERSION,
        "session_id": report.room_id,
        "job_id": report.job_id,
        "room_name": report.room,
        "started_at": report.started_at,
        "ended_at": report.timestamp,
        "duration": duration,
        "agent_name": AGENT_NAME,
        "language": config.language,
        "scenario": config.scenario.id,
        "report": report_data,
    }


def _post_json(url: str, token: str, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "voice-demo-observability/1",
        },
    )
    with urllib.request.urlopen(request, timeout=UPLOAD_TIMEOUT_SECONDS) as response:
        if response.status != 204:
            raise RuntimeError(f"unexpected observability response: {response.status}")


async def upload_session_artifact(
    artifact: dict[str, Any],
    url: str,
    token: str,
) -> None:
    """Sube el artefacto sin bloquear el event loop del agente."""

    await asyncio.to_thread(_post_json, url, token, artifact)


async def persist_session_observability(ctx: JobContext) -> None:
    """Genera y persiste transcript, tools y métricas cuando termina la sesión."""

    url = os.getenv(OBSERVABILITY_URL_ENV)
    token = os.getenv(OBSERVABILITY_TOKEN_ENV)
    if not url or not token:
        logger.warning("voice observability is not configured; session was not persisted")
        return

    try:
        report = ctx.make_session_report()
        artifact = build_session_artifact(report, ctx.job.metadata)
        await upload_session_artifact(artifact, url, token)
        logger.info(
            "voice observability persisted",
            extra={"session_id": report.room_id, "job_id": report.job_id},
        )
    except (OSError, RuntimeError, ValueError, urllib.error.URLError):
        logger.exception("voice observability persistence failed")
