#!/bin/bash
set -e

export DEBIAN_FRONTEND=noninteractive

echo "📦 Installo dipendenze di sistema..."
apt update && apt install -y python3-pip python3.10 python3.10-dev git libgl1 libglib2.0-0 wget unzip curl

echo "🐍 Installo dipendenze Python..."
pip3 install --upgrade pip
pip3 install -r /workspace/ai-car-3d-backend/requirements.txt

echo "📦 Scarico e installo Meshroom..."
cd /workspace
wget https://github.com/alicevision/meshroom/releases/download/v2021.1.0/Meshroom-2021.1.0-linux.tar.gz
tar -xzf Meshroom-2021.1.0-linux.tar.gz
mv Meshroom-2021.1.0 /opt/meshroom
export PATH="/opt/meshroom:$PATH"

echo "🚀 Avvio FastAPI..."
cd /workspace/ai-car-3d-backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
