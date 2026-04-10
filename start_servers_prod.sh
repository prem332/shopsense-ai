#!/bin/bash

echo "Starting ShopSense AI - Production"
echo "==================================="

# Start A2A Agent Servers in background
echo "Starting GuardrailsAgent (port 8001)..."
uvicorn app.backend.a2a.servers.guardrails_server:app \
  --host 0.0.0.0 --port 8001 &

echo "Starting PreferenceAgent (port 8002)..."
uvicorn app.backend.a2a.servers.preference_server:app \
  --host 0.0.0.0 --port 8002 &

echo "Starting SearchRankAgent (port 8003)..."
uvicorn app.backend.a2a.servers.search_server:app \
  --host 0.0.0.0 --port 8003 &

echo "Starting AlertAgent (port 8004)..."
uvicorn app.backend.a2a.servers.alert_server:app \
  --host 0.0.0.0 --port 8004 &

# Wait for agents to initialize
echo "Waiting for agents to initialize (15 seconds)..."
sleep 15

# Start main FastAPI server
# Cloud Run injects PORT env variable
echo "Starting Main Server..."
echo "==================================="
PORT=${PORT:-8000}
uvicorn app.backend.main:app \
  --host 0.0.0.0 \
  --port $PORT