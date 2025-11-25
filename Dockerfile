FROM python:3.11-slim-bullseye

# Diretório de trabalho dentro do container
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    software-properties-common \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código da aplicação
COPY . .

# Expor porta para o Streamlit
EXPOSE 8502

# Healthcheck para verificar se o Streamlit está rodando
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl --fail http://localhost:8502/_stcore/health || exit 1

# Iniciar app Streamlit
ENTRYPOINT ["streamlit", "run", "main_app.py", "--server.port=8502", "--server.address=0.0.0.0"]
