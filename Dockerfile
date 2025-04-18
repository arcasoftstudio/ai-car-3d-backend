FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

# Evita prompt durante installazione
ENV DEBIAN_FRONTEND=noninteractive

# Installa dipendenze
RUN apt-get update && \
    apt-get install -y python3-pip python3.10 python3.10-dev wget git unzip curl \
    libgl1-mesa-glx libglib2.0-0 && \
    ln -s /usr/bin/python3.10 /usr/bin/python && \
    pip install --upgrade pip

# Installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Installa Meshroom (precompilato)
RUN wget https://github.com/alicevision/meshroom/releases/download/v2021.1.0/Meshroom-2021.1.0-linux.tar.gz && \
    tar -xzf Meshroom-2021.1.0-linux.tar.gz && \
    mv Meshroom-2021.1.0 /opt/meshroom

ENV PATH="/opt/meshroom:$PATH"

# Copia il codice
COPY . /app
WORKDIR /app

# Avvio
CMD ["./start.sh"]
