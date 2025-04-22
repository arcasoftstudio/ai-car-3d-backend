#!/bin/bash
set -e

export DEBIAN_FRONTEND=noninteractive
echo "✅ START.SH INIZIATO"

echo "🧱 Installo dipendenze di sistema..."
apt update && apt install -y python3-pip git libgl1 libglib2.0-0 build-essential wget unzip curl

echo "🐍 Upgrade pip e installo requirements Python..."
pip3 install --upgrade pip
pip3 install -r /workspace/ai-car-3d-backend/requirements.txt

echo "📦 Scarico Meshroom da Hugging Face..."
cd /workspace
wget https://huggingface.co/ArcaSoftSrudio/ai-car-business/resolve/main/Meshroom-2021.1.0-linux-cuda10.tar.gz

echo "📂 Estrazione Meshroom..."
mkdir -p /opt/meshroom
tar -xzf Meshroom-2021.1.0-linux-cuda10.tar.gz -C /opt/meshroom --no-same-owner

echo "🗂️ Contenuto estratto:"
ls -l /opt/meshroom

echo "🔐 Rendo eseguibile meshroom_photogrammetry..."
chmod +x /opt/meshroom/Meshroom-*/meshroom_photogrammetry || echo "❌ File non trovato"

echo "🔗 Creo link simbolico globale..."
ln -sf /opt/meshroom/Meshroom-*/meshroom_photogrammetry /usr/local/bin/meshroom_photogrammetry

echo "🚀 Avvio FastAPI sulla porta 8000..."
cd /workspace/ai-car-3d-backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
