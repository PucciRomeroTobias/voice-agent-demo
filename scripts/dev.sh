#!/usr/bin/env zsh

set -eu

repo_dir="${0:A:h:h}"
cd "$repo_dir"

if [[ ! -f .env.local ]]; then
  print -u2 "Falta .env.local con las credenciales de LiveKit."
  exit 1
fi

set -a
source .env.local
set +a

cleanup() {
  kill "$agent_pid" "$web_pid" 2>/dev/null || true
}

uv run python src/agent.py dev &
agent_pid=$!

(
  cd web
  npm run dev
) &
web_pid=$!

trap cleanup EXIT INT TERM

wait "$agent_pid"
wait "$web_pid"
