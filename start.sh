#!/bin/bash
set -e

echo "✅ Avvio ambiente FastAPI + Meshroom"

# Attiva variabili Meshroom (opzionale se già in Dockerfile)
export PATH="/opt/meshroom:$PATH"
export LD_LIBRARY_PATH="/opt/meshroom/aliceVision/lib:$LD_LIBRARY_PATH"

# Avvia FastAPI (backend)
uvicorn app.main:app --host 0.0.0.0 --port 8000
