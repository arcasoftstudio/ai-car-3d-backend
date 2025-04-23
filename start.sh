#!/bin/bash
set -e

echo "✅ Avvio ambiente FastAPI + Meshroom"

# Assicura che pip e uvicorn siano presenti
python3 -m pip show uvicorn || python3 -m pip install uvicorn

# Imposta path di Meshroom se necessario
export PATH="/opt/meshroom:$PATH"
export LD_LIBRARY_PATH="/opt/meshroom/aliceVision/lib:$LD_LIBRARY_PATH"

# Lancia FastAPI
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
