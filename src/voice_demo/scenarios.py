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
                "Atendés la recepción de una clínica ficticia. Identificá si la "
                "consulta requiere gestión administrativa y, cuando corresponda, "
                "usá la herramienta de reserva. No brindes consejos médicos ni "
                "uses datos personales: el turno mock ya usa datos de prueba."
            ),
            "en": (
                "You handle reception for a fictional clinic. Identify whether the "
                "request needs administrative handling and, when appropriate, use "
                "the booking tool. Do not provide medical advice or collect personal "
                "data: the mock appointment already uses test data."
            ),
        },
        greetings={
            "es": "Hola, soy el asistente de la clínica. ¿En qué puedo ayudarte?",
            "en": "Hello, I am the clinic assistant. How can I help you?",
        },
        test_data={"appointment_slot": "martes 10:30", "service": "consulta general"},
        tool_name="reserve_appointment",
        outcome={
            "type": "appointment_reserved",
            "summary": "Turno de prueba reservado para martes 10:30.",
        },
    ),
    "saas_b2b": ScenarioDefinition(
        id="saas_b2b",
        label="SaaS B2B",
        tts_voice="Ashley",
        prompts={
            "es": (
                "Calificás leads para un SaaS B2B ficticio. Confirmá interés, "
                "problema y ajuste general; cuando haya señales suficientes, usá la "
                "herramienta para crear el lead calificado. No recopiles datos de "
                "contacto ni empresa: el mock usa datos de prueba."
            ),
            "en": (
                "You qualify leads for a fictional B2B SaaS. Confirm interest, pain "
                "point, and general fit; when there are enough signals, use the "
                "tool to create the qualified lead. Do not collect contact or company "
                "data: the mock uses test data."
            ),
        },
        greetings={
            "es": "Hola, soy el asistente de la demo SaaS. ¿Qué problema querés resolver?",
            "en": "Hello, I am the SaaS demo assistant. What problem would you like to solve?",
        },
        test_data={"demo_slot": "jueves 15:00", "lead_segment": "equipo de 50 personas"},
        tool_name="create_qualified_lead",
        outcome={
            "type": "qualified_lead_created",
            "summary": "Lead de prueba calificado y demo agendada para jueves 15:00.",
        },
    ),
    "support": ScenarioDefinition(
        id="support",
        label="Soporte",
        tts_voice="Olivia",
        prompts={
            "es": (
                "Hacés diagnóstico inicial de soporte para un producto ficticio. "
                "Aclarás el problema con pasos breves y, cuando corresponde una "
                "revisión humana, usá la herramienta de escalamiento. No solicites "
                "datos personales ni acceso a sistemas."
            ),
            "en": (
                "You provide first-line support for a fictional product. Clarify "
                "the issue with brief steps and, when human review is appropriate, "
                "use the escalation tool. Do not request personal data or system access."
            ),
        },
        greetings={
            "es": "Hola, soy el asistente de soporte. Contame qué está pasando.",
            "en": "Hello, I am the support assistant. Tell me what is happening.",
        },
        test_data={"case_id": "SUP-042", "queue": "especialistas de producto"},
        tool_name="escalate_support_case",
        outcome={
            "type": "support_case_escalated",
            "summary": "Caso de prueba SUP-042 escalado a especialistas de producto.",
        },
    ),
}


@dataclass
class ScenarioSession:
    """Estado en memoria de un escenario, creado nuevamente para cada llamada."""

    definition: ScenarioDefinition
    used_tools: list[str] = field(default_factory=list)

    def record_tool_use(self) -> dict[str, Any]:
        if self.definition.tool_name not in self.used_tools:
            self.used_tools.append(self.definition.tool_name)
        return self.result()

    def result(self) -> dict[str, Any]:
        """Resultado seguro para que la UI lo muestre al finalizar la llamada."""

        return {
            "scenario": self.definition.id,
            "tools_used": list(self.used_tools),
            "outcome": self.definition.outcome if self.used_tools else None,
        }


def tools_for(session: ScenarioSession) -> list[Callable[..., Any]]:
    """Crea sólo la herramienta autorizada por el escenario de esta sesión."""

    if session.definition.id == "clinic":

        @function_tool(
            name="reserve_appointment",
            description="Reserva el único turno de prueba disponible de la clínica.",
        )
        async def reserve_appointment() -> dict[str, Any]:
            return session.record_tool_use()

        return [reserve_appointment]

    if session.definition.id == "saas_b2b":

        @function_tool(
            name="create_qualified_lead",
            description="Crea el lead de prueba calificado y agenda su demo.",
        )
        async def create_qualified_lead() -> dict[str, Any]:
            return session.record_tool_use()

        return [create_qualified_lead]

    @function_tool(
        name="escalate_support_case",
        description="Escala el caso de prueba a especialistas de producto.",
    )
    async def escalate_support_case() -> dict[str, Any]:
        return session.record_tool_use()

    return [escalate_support_case]
