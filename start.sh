#!/bin/bash

set -e
export DEBIAN_FRONTEND=noninteractive

# Pulizia
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

echo "📥 Clonazione COLMAP 3.11..."
git clone --branch 3.11 https://github.com/colmap/colmap.git /workspace/colmap

echo "⚙️ Compilazione COLMAP..."
cd /workspace/colmap
mkdir build && cd build
cmake ..
make -j$(nproc)
make install

echo "🚀 Avvio FastAPI..."
cd /workspace/ai-car-3d-backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
