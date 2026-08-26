"""Escenarios de negocio y mocks efímeros de la demo."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Literal

from livekit.agents import function_tool

ScenarioId = Literal["clinic", "saas_b2b", "support"]

DEFAULT_SCENARIO: ScenarioId = "clinic"


@dataclass(frozen=True)
class ScenarioDefinition:
    """Configuración estática de una de las demos de negocio."""

    id: ScenarioId
    label: str
    tts_voice: str
    prompts: dict[str, str]
    greetings: dict[str, str]
    test_data: dict[str, str]
    tool_name: str
    outcome: dict[str, str]


SCENARIOS: dict[ScenarioId, ScenarioDefinition] = {
    "clinic": ScenarioDefinition(
        id="clinic",
        label="Clínica",
        tts_voice="Diego",
        prompts={
            "es": (
                "Atendés la recepción de una clínica ficticia. Tu objetivo es ayudar "
                "a simular una reserva. Primero saludá y entendé el pedido. Antes de "
                "usar reserve_appointment, debés conocer con claridad una fecha y una "
                "hora elegidas por la persona. Si falta cualquiera de esos datos, "
                "preguntalo explícitamente; nunca inventes ni propongas un horario fijo. "
                "La herramienta sólo simula el éxito: no hay agenda ni reserva real. "
                "No brindes consejos médicos ni solicites datos personales."
            ),
            "en": (
                "You handle reception for a fictional clinic. Help simulate an "
                "appointment booking. Before using reserve_appointment, you must know "
                "a date and time chosen by the person. If either is missing, ask for "
                "it explicitly; never invent or offer a fixed slot. The tool only "
                "simulates success: no calendar or real booking exists. Do not provide "
                "medical advice or collect personal data."
            ),
        },
        greetings={
            "es": (
                "Hola, buenas. Soy un agente virtual para ayudar a reservar turnos "
                "en esta clínica. ¿Para qué fecha y hora te gustaría reservar?"
            ),
            "en": (
                "Hello. I am a virtual agent here to help book appointments at this "
                "clinic. What date and time would you like to reserve?"
            ),
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
        tts_voice="Ashley",
        prompts={
            "es": (
                "Atendés reservas de demos para un SaaS B2B ficticio. Antes de usar "
                "create_qualified_lead, debés conocer la necesidad principal, la fecha "
                "y la hora de la demo. Si falta alguno, preguntalo explícitamente; no "
                "inventes datos ni propongas un horario fijo. La herramienta sólo "
                "simula el éxito: no crea un lead ni agenda una demo real. No recopiles "
                "datos de contacto ni empresa."
            ),
            "en": (
                "You arrange demo reservations for a fictional B2B SaaS. Before using "
                "create_qualified_lead, you must know the person's main need and the "
                "demo date and time. Ask explicitly for any missing field; do not "
                "invent data or offer a fixed slot. The tool only simulates success: "
                "it does not create a lead or schedule a real demo. Do not collect "
                "contact or company data."
            ),
        },
        greetings={
            "es": (
                "Hola, buenas. Soy un agente virtual para ayudar a reservar una demo "
                "de nuestro SaaS. ¿Cuál es tu necesidad principal y qué fecha y hora "
                "te resultan cómodas?"
            ),
            "en": (
                "Hello. I am a virtual agent here to help reserve a demo of our SaaS. "
                "What is your main need, and what date and time work for you?"
            ),
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
        tts_voice="Olivia",
        prompts={
            "es": (
                "Hacés diagnóstico inicial para el soporte de un producto ficticio. "
                "Antes de usar escalate_support_case, debés conocer el área afectada, "
                "el impacto y una breve descripción del problema. Si falta algún dato, "
                "preguntalo explícitamente; nunca lo inventes. La herramienta sólo "
                "simula el éxito: no crea un caso real. No solicites datos personales "
                "ni acceso a sistemas."
            ),
            "en": (
                "You provide initial support for a fictional product. Before using "
                "escalate_support_case, you must know the affected area, impact, and "
                "a brief issue description. Ask explicitly for any missing data; never "
                "invent it. The tool only simulates success: it does not create a real "
                "case. Do not request personal data or system access."
            ),
        },
        greetings={
            "es": (
                "Hola, buenas. Soy un agente virtual para ayudar con soporte. Contame "
                "brevemente qué problema tenés y en qué área ocurre."
            ),
            "en": (
                "Hello. I am a virtual agent here to help with support. Briefly tell "
                "me what problem you have and which area it affects."
            ),
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
    used_tools: list[str] = field(default_factory=list)
    details: dict[str, str] | None = None

    def record_tool_use(self, details: dict[str, str]) -> dict[str, Any]:
        if self.definition.tool_name not in self.used_tools:
            self.used_tools.append(self.definition.tool_name)
        self.details = details
        return self.result()

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


def tools_for(session: ScenarioSession) -> list[Callable[..., Any]]:
    """Crea sólo la herramienta autorizada por el escenario de esta sesión."""

    if session.definition.id == "clinic":

        @function_tool(
            name="reserve_appointment",
            description=(
                "Simula una reserva con una fecha y una hora indicadas por la persona. "
                "Ambos parámetros son obligatorios. No crea una reserva real."
            ),
        )
        async def reserve_appointment(
            appointment_date: str,
            appointment_time: str,
        ) -> dict[str, Any]:
            return session.record_tool_use(
                {
                    "appointment_date": appointment_date,
                    "appointment_time": appointment_time,
                }
            )

        return [reserve_appointment]

    if session.definition.id == "saas_b2b":

        @function_tool(
            name="create_qualified_lead",
            description=(
                "Simula la reserva de una demo. Requiere necesidad principal, fecha y "
                "hora elegidas por la persona. No crea un lead ni agenda una demo real."
            ),
        )
        async def create_qualified_lead(
            primary_need: str,
            demo_date: str,
            demo_time: str,
        ) -> dict[str, Any]:
            return session.record_tool_use(
                {
                    "primary_need": primary_need,
                    "demo_date": demo_date,
                    "demo_time": demo_time,
                }
            )

        return [create_qualified_lead]

    @function_tool(
        name="escalate_support_case",
        description=(
            "Simula el escalamiento de un problema. Requiere área afectada, impacto y "
            "una descripción breve. No crea un caso real."
        ),
    )
    async def escalate_support_case(
        issue_area: str,
        severity: str,
        issue_summary: str,
    ) -> dict[str, Any]:
        return session.record_tool_use(
            {
                "issue_area": issue_area,
                "severity": severity,
                "issue_summary": issue_summary,
            }
        )

    return [escalate_support_case]
