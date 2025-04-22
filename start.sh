#!/bin/bash
set -e

export DEBIAN_FRONTEND=noninteractive
echo "✅ START.SH INIZIATO"

echo "🧱 Installo dipendenze di sistema..."
apt update && apt install -y python3-pip git libgl1 libglib2.0-0 build-essential wget unzip curl

echo "🐍 Upgrade pip e installo requirements Python..."
pip3 install --upgrade pip
pip3 install -r /workspace/ai-car-3d-backend/requirements.txt

echo "📦 Scarico Meshroom 2023.3.0 da Hugging Face..."
cd /workspace
wget https://huggingface.co/ArcaSoftSrudio/ai-car-business/resolve/main/Meshroom-2023.3.0-linux.tar.gz -O Meshroom.tar.gz

echo "📂 Estrazione Meshroom..."
mkdir -p /opt/meshroom
tar -xzf Meshroom.tar.gz -C /opt/meshroom --no-same-owner

echo "🔎 Cerco meshroom_photogrammetry nel filesystem..."
BIN_PATH=$(find /opt/meshroom -type f -name "meshroom_photogrammetry" | head -n 1)

if [ -z "$BIN_PATH" ]; then
    echo "❌ meshroom_photogrammetry non trovato!"
    exit 1
else
    echo "✅ Trovato: $BIN_PATH"
    chmod +x "$BIN_PATH"
    ln -sf "$BIN_PATH" /usr/local/bin/meshroom_photogrammetry
fi

echo "🚀 Avvio FastAPI sulla porta 8000..."
cd /workspace/ai-car-3d-backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
