FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY ml/ ./ml/
COPY decision_engine/ ./decision_engine/
COPY entrypoint.sh .
COPY data/raw/train_FD001.txt ./data/raw/train_FD001.txt

RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
