#!/bin/bash
echo "🔥 Avvio AI CAR 3D BACKEND..."
cd /app
uvicorn app.main:app --host 0.0.0.0 --port 8000
