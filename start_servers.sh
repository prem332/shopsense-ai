#!/bin/bash

echo "🚀 Starting ShopSense AI — All Servers"
echo "======================================"

cd /workspaces/shopsense-ai
source venv/bin/activate

# Kill any existing servers
pkill -f "uvicorn" 2>/dev/null
sleep 2

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

# Wait longer for HuggingFace model to load
echo "Waiting for agents to initialize (15 seconds)..."
sleep 15

# Start main FastAPI server
echo "Starting Main Server (port 8000)..."
uvicorn app.backend.main:app \
  --reload --host 0.0.0.0 --port 8000
