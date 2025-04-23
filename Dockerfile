FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

# Evita prompt durante installazione
ENV DEBIAN_FRONTEND=noninteractive

# Installa dipendenze di sistema
RUN apt-get update && \
    apt-get install -y python3-pip python3.10 python3.10-dev wget git unzip curl \
    libgl1-mesa-glx libglib2.0-0 libpng-dev libjpeg-dev libtiff-dev && \
    ln -s /usr/bin/python3.10 /usr/bin/python && \
    pip install --upgrade pip && \
    rm -rf /var/lib/apt/lists/*

# Installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installa Meshroom (precompilato, versione 2023.2.0)
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
RUN chmod +x start.sh

# Avvio
CMD ["./start.sh"]
