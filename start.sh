#!/bin/bash

set -e
export DEBIAN_FRONTEND=noninteractive

# ❌ Pulisce eventuali cartelle da tentativi precedenti
rm -rf /workspace/colmap /workspace/uploads /workspace/outputs

echo "🔧 Aggiornamento sistema e installazione dipendenze..."
apt update && apt install -y \
    git cmake build-essential wget unzip \
    libboost-all-dev libeigen3-dev libsuitesparse-dev \
    qtbase5-dev libglew-dev freeglut3-dev \
    libatlas-base-dev libopencv-dev \
    libfreeimage-dev libflann-dev



echo "📥 Clonazione COLMAP..."
git clone https://github.com/colmap/colmap.git /workspace/colmap

echo "⚙️ Compilazione COLMAP..."
cd /workspace/colmap
mkdir build && cd build
cmake ..
make -j8
make install

echo "🚀 Avvio FastAPI..."
cd /workspace
uvicorn app.main:app --host 0.0.0.0 --port 8000
