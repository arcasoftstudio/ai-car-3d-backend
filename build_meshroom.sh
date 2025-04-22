#!/bin/bash
set -e

echo "🔧 Imposto modalità non interattiva per apt..."
export DEBIAN_FRONTEND=noninteractive
export TZ=Etc/UTC
ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime

echo "🔧 Aggiorno e installo dipendenze..."
apt update && apt install -y tzdata && dpkg-reconfigure -f noninteractive tzdata
apt install -y \
    git cmake build-essential libboost-all-dev libeigen3-dev libopenimageio-dev \
    libpng-dev libjpeg-dev libtiff-dev libraw-dev libopenexr-dev \
    libopencv-dev qtbase5-dev libglew-dev

echo "🐙 Clono AliceVision..."
git clone --recursive https://github.com/alicevision/AliceVision.git
cd AliceVision
mkdir build && cd build

echo "🛠️ Compilo AliceVision (potrebbe impiegare 10–15 min)..."
cmake .. -DCMAKE_BUILD_TYPE=Release -DALICEVISION_USE_CUDA=ON
make -j$(nproc)

echo "✅ Compilato. File pronto in:"
ls install/bin/meshroom_photogrammetry
