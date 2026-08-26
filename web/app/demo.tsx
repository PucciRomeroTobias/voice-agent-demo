"use client";

import {
  RoomAudioRenderer,
  SessionProvider,
  StartAudio,
  useAgent,
  useSession,
  useSessionMessages,
} from "@livekit/components-react";
import { RoomEvent, TokenSource } from "livekit-client";
import { useEffect, useMemo, useState } from "react";

type Language = "es" | "en";
type ScenarioId = "clinic" | "saas_b2b" | "support";
type DemoConfig = { language: Language; scenario: ScenarioId };
type DemoResult = {
  scenario: ScenarioId;
  tools_used: string[];
  outcome: { type: string; summary: string; details?: Record<string, string> } | null;
};

const scenarios: Record<
  ScenarioId,
  { label: string; description: string; tool: string }
> = {
  clinic: {
    label: "Clínica",
    description: "Gestioná una consulta administrativa y reservá un turno.",
    tool: "Reserva de turno",
  },
  saas_b2b: {
    label: "SaaS B2B",
    description: "Calificá un lead y agendá una demo.",
    tool: "Lead calificado",
  },
  support: {
    label: "Soporte",
    description: "Hacé un diagnóstico inicial y escalá el caso.",
    tool: "Escalamiento",
  },
};

function isDemoResult(value: unknown): value is DemoResult {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<DemoResult>;
  return (
    typeof candidate.scenario === "string" &&
    Array.isArray(candidate.tools_used) &&
    (candidate.outcome === null ||
      (typeof candidate.outcome === "object" &&
        typeof candidate.outcome.summary === "string"))
  );
}

function CallPanel({
  session,
  onEnd,
}: {
  session: ReturnType<typeof useSession>;
  onEnd: () => Promise<void>;
}) {
  const agent = useAgent();
  const { messages } = useSessionMessages();

  return (
    <section className="call-panel" aria-live="polite">
      <RoomAudioRenderer />
      <StartAudio label="Activar audio" />
      <div className="status-row">
        <span className="status-dot" />
        <span>{agent.state === "listening" ? "Escuchando" : agent.state}</span>
        <button className="secondary" onClick={() => void onEnd()} type="button">
          Terminar llamada
        </button>
      </div>
      <div className="transcript" aria-label="Transcripción de la llamada">
        {messages.length === 0 ? (
          <p>Conectando la conversación…</p>
        ) : (
          messages.map((message) => (
            <p key={message.id} className={message.type === "agentTranscript" ? "agent" : ""}>
              {message.message}
            </p>
          ))
        )}
      </div>
      {!session.isConnected && <p className="muted">Desconectando…</p>}
    </section>
  );
}

export function Demo() {
  const [language, setLanguage] = useState<Language>("es");
  const [scenario, setScenario] = useState<ScenarioId>("clinic");
  const [activeConfig, setActiveConfig] = useState<DemoConfig | null>(null);
  const [result, setResult] = useState<DemoResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const requestedConfig = useMemo(
    () => activeConfig ?? { language, scenario },
    [activeConfig, language, scenario],
  );

  const tokenSource = useMemo(
    () =>
      TokenSource.custom(async (options) => {
        const response = await fetch("/api/livekit-token", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...options, ...requestedConfig }),
        });
        if (!response.ok) {
          throw new Error("No se pudo iniciar la sesión. Intentá nuevamente.");
        }
        return response.json();
      }),
    [requestedConfig],
  );
  const session = useSession(tokenSource, { agentName: "voice-demo" });

  useEffect(() => {
    const receiveResult = (
      payload: Uint8Array,
      _participant: unknown,
      _kind: unknown,
      topic?: string,
    ) => {
      if (topic !== "voice-demo-result") return;
      try {
        const parsed: unknown = JSON.parse(new TextDecoder().decode(payload));
        if (isDemoResult(parsed)) setResult(parsed);
      } catch {
        // Los paquetes de datos ajenos a la UI se ignoran de forma segura.
      }
    };
    session.room.on(RoomEvent.DataReceived, receiveResult);
    return () => {
      session.room.off(RoomEvent.DataReceived, receiveResult);
    };
  }, [session.room]);

  async function startCall() {
    setError(null);
    setResult(null);
    const config = requestedConfig;
    setActiveConfig(config);
    try {
      await session.start({ tracks: { microphone: { enabled: true } } });
    } catch (startError) {
      setActiveConfig(null);
      setError(startError instanceof Error ? startError.message : "No se pudo conectar.");
    }
  }

  async function endCall() {
    await session.end();
    setActiveConfig(null);
  }

  const isInCall = activeConfig !== null;
  const hasDeferredLanguageChange = isInCall && language !== activeConfig.language;

  return (
    <main>
      <header>
        <p className="eyebrow">Voice Agent · LiveKit</p>
        <h1>Una conversación de negocio, no un guion.</h1>
        <p className="intro">
          Elegí un escenario. El agente escucha, decide y ejecuta una acción mock
          con resultado visible.
        </p>
      </header>
      <section className="controls" aria-label="Configuración de la demo">
        <label>
          Idioma general
          <select value={language} onChange={(event) => setLanguage(event.target.value as Language)}>
            <option value="es">Español</option>
            <option value="en">English</option>
          </select>
        </label>
        <fieldset disabled={isInCall}>
          <legend>Escenario</legend>
          <div className="scenario-grid">
            {(Object.keys(scenarios) as ScenarioId[]).map((id) => (
              <label className={scenario === id ? "scenario selected" : "scenario"} key={id}>
                <input checked={scenario === id} name="scenario" onChange={() => setScenario(id)} type="radio" value={id} />
                <span>{scenarios[id].label}</span>
                <small>{scenarios[id].description}</small>
                <em>{scenarios[id].tool}</em>
              </label>
            ))}
          </div>
        </fieldset>
        {hasDeferredLanguageChange && (
          <p className="notice">El nuevo idioma se aplicará al iniciar una sesión nueva.</p>
        )}
      </section>
      <SessionProvider session={session}>
        {isInCall ? (
          <CallPanel onEnd={endCall} session={session} />
        ) : (
          <button className="primary" onClick={() => void startCall()} type="button">
            Iniciar demo de voz
          </button>
        )}
      </SessionProvider>
      {error && <p className="error">{error}</p>}
      <section className="summary" aria-live="polite">
        <p className="eyebrow">Resultado de negocio</p>
        {result?.outcome ? (
          <>
            <h2>{scenarios[result.scenario].label}</h2>
            <p>{result.outcome.summary}</p>
            {result.outcome.details && (
              <p className="muted">
                Datos simulados: {Object.entries(result.outcome.details)
                  .map(([key, value]) => `${key}: ${value}`)
                  .join(" · ")}
              </p>
            )}
            <p className="muted">Herramienta usada: {result.tools_used.join(", ")}</p>
          </>
        ) : (
          <p className="muted">El resultado aparecerá al usar la herramienta mock durante la llamada.</p>
        )}
      </section>
    </main>
  );
}
