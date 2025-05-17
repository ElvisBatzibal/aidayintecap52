FROM postgres:latest

# Instalar las dependencias necesarias para compilar la extensión
RUN apt-get update && apt-get install -y \
    postgresql-server-dev-all \
    build-essential \
    git && \
    rm -rf /var/lib/apt/lists/*

# Clonar, compilar e instalar la extensión pgvector
RUN git clone https://github.com/pgvector/pgvector.git /tmp/pgvector && \
    cd /tmp/pgvector && \
    make && \
    make install && \
    rm -rf /tmp/pgvector