#!/bin/bash

set -e
export DEBIAN_FRONTEND=noninteractive

# Pulizia cartelle vecchie
rm -rf /workspace/colmap /workspace/uploads /workspace/outputs /workspace/status

echo "🔧 Installazione dipendenze di sistema..."
apt update && apt install -y \
    git cmake build-essential wget unzip python3-pip \
    libboost-all-dev libeigen3-dev libsuitesparse-dev \
    qtbase5-dev libglew-dev freeglut3-dev \
    libatlas-base-dev libopencv-dev \
    libfreeimage-dev libflann-dev \
    libsqlite3-dev libceres-dev libcgal-dev \
    libgflags-dev libgoogle-glog-dev libmetis-dev

echo "🐍 Installazione dipendenze Python..."
pip install --upgrade pip
pip install -r /workspace/ai-car-3d-backend/requirements.txt

echo "📥 Download COLMAP 3.11.1 da Hugging Face..."
wget https://huggingface.co/ArcaSoftSrudio/ai-car-business/resolve/main/colmap-3.11.1.tar.gz -O /workspace/colmap-3.11.1.tar.gz

echo "📂 Estrazione COLMAP 3.11.1..."
tar -xzf /workspace/colmap-3.11.1.tar.gz -C /workspace/
mv /workspace/colmap-3.11.1 /workspace/colmap

echo "⚙️ Compilazione COLMAP..."
cd /workspace/colmap
mkdir build && cd build
cmake ..
make -j$(nproc)
make install

echo "🚀 Avvio FastAPI..."
cd /workspace/ai-car-3d-backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
