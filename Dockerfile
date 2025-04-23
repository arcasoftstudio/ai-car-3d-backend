FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

# Evita prompt durante installazione
ENV DEBIAN_FRONTEND=noninteractive

# Installa Python + dipendenze di sistema
RUN apt-get update && \
    apt-get install -y python3 python3-dev python3-pip wget git unzip curl \
    libgl1-mesa-glx libglib2.0-0 libpng-dev libjpeg-dev libtiff-dev \
    libopencv-dev python3-opencv \
    qt5-default libqt5x11extras5-dev \
    libx11-dev && \
    rm -rf /var/lib/apt/lists/*

# Installa dipendenze Python
COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt

# Installa Meshroom (precompilato)
RUN wget https://github.com/alicevision/meshroom/releases/download/v2023.2.0/Meshroom-2023.2.0-linux-cuda.tar.gz && \
    tar -xzf Meshroom-2023.2.0-linux-cuda.tar.gz && \
    mv Meshroom-2023.2.0 /opt/meshroom && \
    rm Meshroom-2023.2.0-linux-cuda.tar.gz

# Imposta variabili d'ambiente per Meshroom
ENV PATH="/opt/meshroom:$PATH"
ENV LD_LIBRARY_PATH="/opt/meshroom/aliceVision/lib:${LD_LIBRARY_PATH}"

# Copia il codice
COPY . /app
WORKDIR /app

# Rendi eseguibile lo script di avvio
RUN chmod +x /app/start.sh

# Avvio
ENTRYPOINT ["./start.sh"]
