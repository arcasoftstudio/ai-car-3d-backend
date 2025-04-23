#!/bin/bash
set -e
export DEBIAN_FRONTEND=noninteractive

echo "🧹 Pulizia iniziale..."
rm -rf /workspace/AliceVision /workspace/Meshroom-2023.3.0 /workspace/nanoflann /workspace/input_images /workspace/output_model

echo "📦 Installo dipendenze di sistema..."
apt update && apt install -y \
  python3-pip git wget unzip curl \
  build-essential cmake libgl1 libglib2.0-0 \
  libpng-dev libjpeg-dev libtiff-dev \
  libboost-all-dev qtbase5-dev \
  libopenexr-dev zlib1g-dev

echo "🐍 Installo pip e requirements Python..."
pip3 install --upgrade pip
pip3 install -r /workspace/ai-car-3d-backend/requirements.txt

echo "📦 Scarico Meshroom da Hugging Face (se non già presente)..."
cd /workspace
if [ ! -d Meshroom-2023.3.0 ]; then
  wget -q https://huggingface.co/ArcaSoftSrudio/ai-car-business/resolve/main/Meshroom-2023.3.0-linux.tar.gz -O meshroom.tar.gz
  tar --no-same-owner -xzf meshroom.tar.gz
  rm meshroom.tar.gz
fi


echo "🔧 Compilo AliceVision con build_meshroom.sh..."
cd /workspace/ai-car-3d-backend
echo "📥 Clono nanoflann (per AliceVision)..."
cd /workspace
git clone https://github.com/jlblancoc/nanoflann.git

cd /workspace/ai-car-3d-backend
chmod +x build_meshroom.sh
bash build_meshroom.sh


echo "🔗 Creo link simbolico per meshroom_photogrammetry..."
ln -sf /workspace/ai-car-3d-backend/AliceVision/build/install/bin/meshroom_photogrammetry /usr/local/bin/meshroom_photogrammetry

echo "🚀 Avvio FastAPI..."
uvicorn app.main:app --host 0.0.0.0 --port 8000
