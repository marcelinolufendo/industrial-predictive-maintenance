FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY ml/ ./ml/
COPY decision_engine/ ./decision_engine/
COPY entrypoint.sh .

RUN chmod +x entrypoint.sh

# Download C-MAPSS FD001 dataset
RUN mkdir -p data/raw && \
    curl -fL "https://raw.githubusercontent.com/hankroark/Turbofan-Engine-Degradation/master/CMaps/train_FD001.txt" \
         -o data/raw/train_FD001.txt

CMD ["./entrypoint.sh"]
