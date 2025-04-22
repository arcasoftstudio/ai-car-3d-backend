#!/bin/bash
set -e

export DEBIAN_FRONTEND=noninteractive
echo "✅ START.SH INIZIATO"

echo "🧱 Installo dipendenze di sistema base..."
apt update && apt install -y python3-pip git libgl1 libglib2.0-0 build-essential wget unzip curl

echo "🐍 Installo pip e requirements Python..."
pip3 install --upgrade pip
pip3 install -r /workspace/ai-car-3d-backend/requirements.txt

echo "🔧 Compilo AliceVision con build_meshroom.sh..."
cd /workspace/ai-car-3d-backend
chmod +x build_meshroom.sh
bash build_meshroom.sh

echo "🔗 Creo link simbolico per meshroom_photogrammetry..."
ln -sf /workspace/ai-car-3d-backend/AliceVision/build/install/bin/meshroom_photogrammetry /usr/local/bin/meshroom_photogrammetry

echo "🚀 Avvio FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port 8000
