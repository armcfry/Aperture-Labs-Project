#!/usr/bin/env bash
# Stop everything: backend (8000), frontend (3998), Ollama (11434), Docker (Postgres + MinIO)
# Usage: ./kill.sh [-reset]

cd "$(dirname "$0")"

echo "Stopping processes on ports 8000, 3998, 11434..."

lsof -ti :8000 | xargs kill -9 2>/dev/null || true
lsof -ti :3998 | xargs kill -9 2>/dev/null || true
lsof -ti :11434 | xargs kill -9 2>/dev/null || true

if [ "$1" = "-reset" ]; then
  echo "Stopping Docker and removing volumes..."
  docker compose down -v
  echo "Stopped everything and removed volumes - DB reset."
else
  echo "Stopping Docker..."
  docker compose down
  echo "Stopped app, Ollama, and Docker."
fi
