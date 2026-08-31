"""Escenarios de negocio y mocks efímeros de la demo."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date as calendar_date
from datetime import timedelta
from typing import Any, Literal

from livekit.agents import function_tool

ScenarioId = Literal["clinic", "saas_b2b", "support"]
Weekday = Literal[
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
]
WEEKDAYS: tuple[Weekday, ...] = (
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"
)

DEFAULT_SCENARIO: ScenarioId = "clinic"


@dataclass(frozen=True)
class ScenarioDefinition:
    """Configuración estática de una de las demos de negocio."""

    id: ScenarioId
    label: str
    tts_voices: dict[str, str]
    prompts: dict[str, str]
    greetings: dict[str, str]
    test_data: dict[str, str]
    tool_name: str
    outcome: dict[str, str]

    def voice_for(self, language: str) -> str:
        """Devuelve la voz evaluada para el idioma de la sesión."""

        return self.tts_voices[language]


SCENARIOS: dict[ScenarioId, ScenarioDefinition] = {
    "clinic": ScenarioDefinition(
        id="clinic",
        label="Clínica",
        tts_voices={"es": "alloy", "en": "alloy"},
        prompts={
            "es": (
                "# Escenario: Clínica\n"
                "Objetivo: ayudar a reservar un turno. Guiá con calma y sin "
                "hacer diagnóstico ni dar consejos médicos.\n"
                "Para reservarlo necesitás una fecha y una hora que la persona haya elegido. "
                "No inventes, supongas ni ofrezcas horarios concretos; si falta un dato, preguntá sólo por ese dato. "
                "Si pregunta qué fechas hay disponibles, decí que hay amplia disponibilidad esta semana y la "
                "próxima, y preguntá qué día y horario prefiere.\n"
                "Si menciona síntomas, urgencias o una emergencia, explicá que este canal no puede dar "
                "atención médica y recomendá comunicarse con un "
                "servicio de emergencias o un profesional local. Volvé a la reserva sólo si corresponde.\n"
                "Después del saludo, si pide ayuda general o algo distinto de un turno, explicá recién "
                "entonces que por este canal sólo podés ayudar a reservar un turno y preguntá si quiere avanzar. "
                "Si quiere reservar, continuá sin explicar limitaciones internas. Podés conservar como "
                "nota opcional una preferencia no personal, por ejemplo especialidad o tipo de profesional; no la "
                "pidas y nunca envíes datos personales a la herramienta."
            ),
            "en": (
                "# Scenario: Clinic\n"
                "Goal: help book an appointment. Guide the person calmly without "
                "diagnosing or giving medical advice.\n"
                "The booking needs a date and time chosen by the person. Never invent, assume, "
                "or offer specific times; if one detail is missing, ask only for that detail. If asked what "
                "dates are available, say there is broad availability this week and next, then ask which day "
                "and time they prefer.\n"
                "If the person mentions symptoms, urgency, or an emergency, explain that this channel "
                "cannot provide medical care and recommend local "
                "emergency services or a qualified professional. Return to booking only when appropriate.\n"
                "After the greeting, only if they ask for general help or something other than an appointment, "
                "then explain that this channel can only help book an appointment and ask whether they want to proceed. "
                "If they want an appointment, continue without explaining internal limitations. You may retain an "
                "optional non-personal preference, such as specialty or type of clinician; never ask for it or send "
                "personal data to the tool."
            ),
        },
        greetings={
            "es": "Hola, gracias por comunicarte con la clínica virtual. ¿En qué puedo ayudarte hoy?",
            "en": "Hello, thanks for calling the virtual clinic. How can I help today?",
        },
        test_data={"appointment_date": "2026-09-10", "appointment_time": "14:30"},
        tool_name="reserve_appointment",
        outcome={
            "type": "appointment_simulated",
            "summary": "Reserva simulada exitosamente; no se creó un turno real.",
        },
    ),
    "saas_b2b": ScenarioDefinition(
        id="saas_b2b",
        label="SaaS B2B",
        tts_voices={"es": "echo", "en": "echo"},
        prompts={
            "es": (
                "# Escenario: SaaS B2B\n"
                "Objetivo: entender qué proceso o necesidad quiere mejorar la persona y reservar una "
                "demo. Mostrá curiosidad genuina, pero no hagas una entrevista comercial ni ventas agresivas.\n"
                "Para reservarla necesitás la necesidad principal y una fecha y hora elegidas por la persona. "
                "No inventes datos ni propongas horarios concretos. Si pregunta qué fechas hay disponibles, "
                "decí que hay amplia disponibilidad esta semana y la próxima, y preguntá qué día y horario "
                "prefiere. Si falta algo, preguntá sólo por el dato faltante.\n"
                "No pidas nombre, empresa, cargo, correo, teléfono ni presupuesto; si solicitan información "
                "comercial específica que no está disponible, decí que no contás con ese dato y volvé a la reserva.\n"
                "Después del saludo, si el pedido es vago o está fuera de este objetivo, explicá recién entonces "
                "que por este canal podés entender su necesidad y reservar una demo, y preguntá si quiere avanzar. "
                "Si expresa una necesidad, avanzá con el siguiente dato faltante. Podés conservar "
                "una nota opcional no personal sobre el contexto o proceso; no la pidas ni envíes datos personales a la herramienta."
            ),
            "en": (
                "# Scenario: B2B SaaS\n"
                "Goal: understand the process or need the person wants to improve and book a "
                "demo. Be genuinely curious, without conducting a sales interrogation or pushing a sale.\n"
                "The booking needs the main need plus a date and time chosen by the person. Never "
                "invent data or offer specific times. If asked what dates are available, say there is broad "
                "availability this week and next, then ask which day and time they prefer. If something is "
                "missing, ask only for that detail.\n"
                "Do not request a name, company, job title, email, phone number, or budget. If asked for "
                "specific commercial information that is unavailable, say you do not have that detail and return to booking.\n"
                "After the greeting, only if the request is vague or outside this objective, then explain that "
                "this channel can understand their need and book a demo, and ask whether they want to continue. "
                "If they state a need, request the next missing detail. You may retain an "
                "optional non-personal note about their context or process; never ask for it or send personal data to the tool."
            ),
        },
        greetings={
            "es": "Hola, gracias por comunicarte con el equipo de soluciones. ¿En qué podemos ayudarte hoy?",
            "en": "Hello, thanks for contacting the solutions team. How can we help today?",
        },
        test_data={"primary_need": "operaciones", "demo_date": "2026-09-11", "demo_time": "10:00"},
        tool_name="create_qualified_lead",
        outcome={
            "type": "lead_qualification_simulated",
            "summary": "Lead de prueba calificado de forma simulada; no se creó un lead ni una demo real.",
        },
    ),
    "support": ScenarioDefinition(
        id="support",
        label="Soporte",
        tts_voices={"es": "nova", "en": "nova"},
        prompts={
            "es": (
                "# Escenario: Soporte\n"
                "Objetivo: hacer un diagnóstico inicial empático y escalar un problema. "
                "Primero reconocé la frustración o el impacto sin culpar a la persona ni prometer una resolución.\n"
                "Para escalarlo necesitás el área afectada, el impacto y una descripción breve. "
                "No inventes ninguno; si falta un dato, preguntá sólo por ese dato y podés ofrecer ejemplos simples de áreas o impacto.\n"
                "No pidas contraseñas, capturas, tokens, datos de cuenta ni que ejecute comandos. "
                "Si aparece un incidente de seguridad, pedí no compartir secretos y recomendá usar el canal seguro correspondiente.\n"
                "Después del saludo, si el pedido es vago o no es un problema de soporte, explicá recién entonces "
                "que por este canal podés hacer un diagnóstico inicial y escalar el problema, y preguntá si quiere avanzar. "
                "Si describe un problema, pedí el siguiente dato faltante. Podés conservar una "
                "nota opcional no personal sobre el contexto del problema; no la pidas ni envíes datos personales a la herramienta."
            ),
            "en": (
                "# Scenario: Support\n"
                "Goal: provide empathetic initial triage and escalate an issue. First "
                "acknowledge the frustration or impact without blaming the person or promising a resolution.\n"
                "The escalation needs the affected area, impact, and a short issue description. Never invent "
                "them; if one is missing, ask only for it and you may offer simple examples of areas or impact.\n"
                "Do not request passwords, screenshots, tokens, account "
                "data, or commands to run. If a security incident arises, ask the person not to share secrets and "
                "recommend the appropriate secure channel.\n"
                "After the greeting, only if the request is vague or not a support issue, then explain that this channel "
                "can perform initial triage and escalate the issue, and ask whether they want to proceed. If they describe "
                "an issue, request the next missing detail. You may retain an optional non-personal note "
                "about the issue context; never ask for it or send personal data to the tool."
            ),
        },
        greetings={
            "es": "Hola, gracias por comunicarte con soporte. ¿En qué puedo ayudarte hoy?",
            "en": "Hello, thanks for contacting support. How can I help today?",
        },
        test_data={"issue_area": "facturación", "severity": "alto", "issue_summary": "Cobro duplicado"},
        tool_name="escalate_support_case",
        outcome={
            "type": "support_escalation_simulated",
            "summary": "Escalamiento de prueba simulado; no se creó un caso real.",
        },
    ),
}


@dataclass
class ScenarioSession:
    """Estado en memoria de un escenario, creado nuevamente para cada llamada."""

    definition: ScenarioDefinition
    local_date: calendar_date | None = None
    used_tools: list[str] = field(default_factory=list)
    details: dict[str, str] | None = None

    def record_tool_use(self, details: dict[str, str]) -> dict[str, Any]:
        if self.definition.tool_name not in self.used_tools:
            self.used_tools.append(self.definition.tool_name)
        self.details = details
        return {"status": "confirmed", "details": details}

    def result(self) -> dict[str, Any]:
        """Resultado seguro para que la UI lo muestre al finalizar la llamada."""

        return {
            "scenario": self.definition.id,
            "tools_used": list(self.used_tools),
            "outcome": (
                {**self.definition.outcome, "details": self.details}
                if self.used_tools
                else None
            ),
        }


def _with_extra_notes(details: dict[str, str], extra_notes: str | None) -> dict[str, str]:
    """Agrega una preferencia opcional sólo cuando la persona la compartió."""

    if extra_notes:
        return {**details, "extra_notes": extra_notes}
    return details


def _require_concrete_schedule(date: str, time: str) -> None:
    """Impide que la tool acepte expresiones relativas sin resolver."""

    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date) is None:
        raise ValueError("date must be a concrete YYYY-MM-DD value")
    try:
        calendar_date.fromisoformat(date)
    except ValueError as error:
        raise ValueError("date must be a valid calendar date") from error
    if re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", time) is None:
        raise ValueError("time must be a concrete 24-hour HH:MM value")


def _resolve_schedule_date(
    absolute_date: str | None,
    weekday: Weekday | None,
    local_date: calendar_date | None,
) -> str:
    """Resuelve un día relativo en código y preserva fechas absolutas explícitas."""

    if (absolute_date is None) == (weekday is None):
        raise ValueError("provide exactly one of absolute date or weekday")
    if weekday is None:
        assert absolute_date is not None
        return absolute_date
    if local_date is None:
        raise ValueError("session local date is required to resolve a weekday")
    days_ahead = (WEEKDAYS.index(weekday) - local_date.weekday()) % 7 or 7
    return (local_date + timedelta(days=days_ahead)).isoformat()


def tools_for(session: ScenarioSession) -> list[Callable[..., Any]]:
    """Crea sólo la herramienta autorizada por el escenario de esta sesión."""

    if session.definition.id == "clinic":

        @function_tool(
            name="reserve_appointment",
            description=(
                "Confirma una reserva con una fecha y una hora indicadas por la persona. "
                "La hora debe ser HH:MM en formato de 24 horas. Si la persona dijo una fecha absoluta, "
                "enviá `appointment_date` como YYYY-MM-DD. Si nombró un día de semana, incluso después de "
                "decir 'next week', DEBÉS enviar sólo `appointment_weekday` en minúsculas y dejar "
                "`appointment_date` vacío; la herramienta resuelve la fecha. `extra_notes` sólo admite "
                "preferencias no personales, por ejemplo especialidad o tipo de profesional."
            ),
        )
        async def reserve_appointment(
            appointment_time: str,
            appointment_date: str | None = None,
            appointment_weekday: Weekday | None = None,
            extra_notes: str | None = None,
        ) -> dict[str, Any]:
            appointment_date = _resolve_schedule_date(
                appointment_date, appointment_weekday, session.local_date
            )
            _require_concrete_schedule(appointment_date, appointment_time)
            return session.record_tool_use(_with_extra_notes(
                {
                    "appointment_date": appointment_date,
                    "appointment_time": appointment_time,
                },
                extra_notes,
            ))

        return [reserve_appointment]

    if session.definition.id == "saas_b2b":

        @function_tool(
            name="create_qualified_lead",
            description=(
                "Confirma la reserva de una demo. Requiere necesidad principal, fecha y "
                "hora elegidas por la persona. La hora debe ser HH:MM. Si dio una fecha absoluta, enviá "
                "`demo_date` como YYYY-MM-DD. Si nombró un día de semana, incluso después de 'next week', "
                "DEBÉS enviar sólo `demo_weekday` en minúsculas y dejar `demo_date` vacío; la herramienta "
                "resuelve la fecha. `extra_notes` sólo admite contexto "
                "no personal sobre el proceso."
            ),
        )
        async def create_qualified_lead(
            primary_need: str,
            demo_time: str,
            demo_date: str | None = None,
            demo_weekday: Weekday | None = None,
            extra_notes: str | None = None,
        ) -> dict[str, Any]:
            demo_date = _resolve_schedule_date(demo_date, demo_weekday, session.local_date)
            _require_concrete_schedule(demo_date, demo_time)
            return session.record_tool_use(_with_extra_notes(
                {
                    "primary_need": primary_need,
                    "demo_date": demo_date,
                    "demo_time": demo_time,
                },
                extra_notes,
            ))

        return [create_qualified_lead]

    @function_tool(
        name="escalate_support_case",
        description=(
            "Confirma el escalamiento de un problema. Requiere área afectada, impacto y "
            "una descripción breve. `extra_notes` es opcional y sólo admite contexto no personal "
            "del problema."
        ),
    )
    async def escalate_support_case(
        issue_area: str,
        severity: str,
        issue_summary: str,
        extra_notes: str | None = None,
    ) -> dict[str, Any]:
        return session.record_tool_use(_with_extra_notes(
            {
                "issue_area": issue_area,
                "severity": severity,
                "issue_summary": issue_summary,
            },
            extra_notes,
        ))

    return [escalate_support_case]
