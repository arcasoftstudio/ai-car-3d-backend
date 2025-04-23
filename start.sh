#!/bin/bash

# Non interattivo
export DEBIAN_FRONTEND=noninteractive

# Aggiorna pacchetti e installa dipendenze
apt update && apt install -y \
    git cmake build-essential wget unzip \
    libboost-all-dev libeigen3-dev libsuitesparse-dev \
    qtbase5-dev libglew-dev freeglut3-dev \
    libatlas-base-dev libopencv-dev

# Installa COLMAP
git clone https://github.com/colmap/colmap.git /workspace/colmap
cd /workspace/colmap
mkdir build && cd build
cmake ..
make -j8
make install

# Torna alla root del progetto
cd /workspace
uvicorn app.main:app --host 0.0.0.0 --port 8000
