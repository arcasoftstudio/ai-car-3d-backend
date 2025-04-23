#!/bin/bash
set -e

echo "🔧 Imposto modalità non interattiva per apt..."
export DEBIAN_FRONTEND=noninteractive
export TZ=Etc/UTC
ln -fs /usr/share/zoneinfo/Etc/UTC /etc/localtime

echo "🔧 Aggiorno e installo dipendenze..."
apt update && apt install -y tzdata && dpkg-reconfigure -f noninteractive tzdata
apt update && apt install -y \
    build-essential cmake git wget curl unzip \
    libboost-all-dev libboost-system-dev libboost-thread-dev \
    libeigen3-dev libopenimageio-dev openimageio-tools \
    libpng-dev libjpeg-dev libtiff-dev libraw-dev libgl1 libglu1-mesa-dev \
    libopenexr-dev libglew-dev libglib2.0-0 libopencv-dev \
    qtbase5-dev qtchooser qt5-qmake qtbase5-dev-tools \
    python3-pip zlib1g-dev pkg-config tzdata

echo "🐙 Clono AliceVision..."
git clone --recursive https://github.com/alicevision/AliceVision.git
cd AliceVision
mkdir build && cd build

echo "🔧 Forzo BOOST manualmente"
export BOOST_ROOT=/usr/include
export Boost_INCLUDE_DIR=/usr/include

echo "🔧 Disattivo check nanoflann nel CMakeLists.txt"
sed -i '/find_package(nanoflann REQUIRED)/d' ../src/CMakeLists.txt
sed -i '/message(FATAL_ERROR "Failed to find nanoflann.")/d' ../src/CMakeLists.txt

echo "🛠️ Compilo AliceVision"
cmake .. -DCMAKE_BUILD_TYPE=Release -DALICEVISION_USE_CUDA=ON
make -j$(nproc)

echo "✅ AliceVision compilato!"
