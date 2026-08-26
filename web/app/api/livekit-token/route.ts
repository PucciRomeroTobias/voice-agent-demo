import { AccessToken, RoomAgentDispatch, RoomConfiguration } from "livekit-server-sdk";

export const runtime = "nodejs";

const LANGUAGES = new Set(["es", "en"]);
const SCENARIOS = new Set(["clinic", "saas_b2b", "support"]);
const TOKEN_TTL_SECONDS = 10 * 60;

type SessionConfig = {
  language: string;
  scenario: string;
};

function badRequest() {
  return Response.json({ error: "Solicitud inválida." }, { status: 400 });
}

function parseSessionConfig(value: unknown): SessionConfig | null {
  if (!value || typeof value !== "object" || Array.isArray(value)) return null;

  const { language, scenario } = value as Record<string, unknown>;
  if (
    typeof language !== "string" ||
    typeof scenario !== "string" ||
    !LANGUAGES.has(language) ||
    !SCENARIOS.has(scenario)
  ) {
    return null;
  }

  return { language, scenario };
}

function getLiveKitConfig() {
  const { LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL } = process.env;
  if (!LIVEKIT_API_KEY || !LIVEKIT_API_SECRET || !LIVEKIT_URL) return null;

  return { apiKey: LIVEKIT_API_KEY, apiSecret: LIVEKIT_API_SECRET, serverUrl: LIVEKIT_URL };
}

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return badRequest();
  }

  const sessionConfig = parseSessionConfig(body);
  if (!sessionConfig) return badRequest();

  const liveKit = getLiveKitConfig();
  if (!liveKit) {
    return Response.json({ error: "La demo no está disponible." }, { status: 503 });
  }

  const roomName = `voice-demo-${crypto.randomUUID()}`;
  const metadata = JSON.stringify(sessionConfig);
  const token = new AccessToken(liveKit.apiKey, liveKit.apiSecret, {
    identity: `visitor-${crypto.randomUUID()}`,
    name: "Demo visitor",
    metadata,
    attributes: sessionConfig,
    ttl: TOKEN_TTL_SECONDS,
  });

  token.addGrant({
    room: roomName,
    roomJoin: true,
    canPublish: true,
    canSubscribe: true,
  });
  token.roomConfig = new RoomConfiguration({
    agents: [
      new RoomAgentDispatch({
        agentName: "voice-demo",
        metadata,
      }),
    ],
  });

  return Response.json({
    server_url: liveKit.serverUrl,
    participant_token: await token.toJwt(),
  });
}
