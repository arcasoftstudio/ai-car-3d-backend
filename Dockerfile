FROM nvidia/cuda:11.7.1-devel-ubuntu20.04

# Imposta variabili e aggiorna sistema
ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /workspace

RUN apt update && apt install -y \
    python3.10 python3.10-venv python3.10-dev python3-pip \
    git cmake build-essential wget unzip \
    libboost-all-dev libeigen3-dev libsuitesparse-dev \
    qtbase5-dev libglew-dev freeglut3-dev \
    libatlas-base-dev libopencv-dev libfreeimage-dev

# Installa Python deps
COPY requirements.txt .
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# Clona e compila COLMAP
RUN git clone https://github.com/colmap/colmap.git /workspace/colmap && \
    cd /workspace/colmap && mkdir build && cd build && \
    cmake .. && make -j8 && make install

# Copia codice progetto
COPY . .

# Comando di avvio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
