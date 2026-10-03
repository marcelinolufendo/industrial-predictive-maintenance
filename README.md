# Industrial Predictive Maintenance & Real-Time Intelligence Platform

Plataforma industrial de manutenção preditiva em tempo real, capaz de receber continuamente dados de sensores, processá-los via streaming, gerar features temporais, executar modelos de Machine Learning e produzir decisões operacionais sobre o estado de cada máquina.

---

## Visão geral

```text
Sensor Simulator (NASA C-MAPSS)
        ↓
      Kafka
        ↓
Spark Structured Streaming
        ↓
  Feature Engineering
        ↓
   Machine Learning
        ↓
  Decision Engine
        ↓
API / Dashboard / Alertas
```

---

## Stack tecnológica

| Camada | Tecnologias |
|---|---|
| Simulação | Python, NASA C-MAPSS |
| Streaming | Apache Kafka, Spark Structured Streaming |
| Data Lake | Delta Lake, Parquet, MinIO (S3-compatible) |
| Machine Learning | Scikit-learn, XGBoost, PyTorch, LSTM |
| MLOps | MLflow Tracking, MLflow Model Registry |
| API | FastAPI, Pydantic |
| Banco operacional | PostgreSQL |
| Observabilidade | Prometheus, Grafana, Alertmanager |
| Infraestrutura | Docker, Docker Compose |

---

## Arquitetura de dados (Medallion)

```text
RAW → BRONZE → SILVER → GOLD
```

- **Bronze** — dados brutos preservados para auditoria e reprocessamento
- **Silver** — dados validados, deduplicados e com schema enforçado
- **Gold** — features temporais prontas para ML e consumo analítico

---

## Casos de uso

- **Monitoramento de condição** — estado atual da máquina: `NORMAL`, `WARNING`, `CRITICAL`
- **Detecção de anomalias** — comportamento fora do padrão esperado
- **Predição de falha** — probabilidade de falha em determinado horizonte
- **Remaining Useful Life (RUL)** — ciclos estimados até condição de falha

---

## Modelos de Machine Learning

| Modelo | Objetivo |
|---|---|
| Isolation Forest | Detecção de anomalias (unsupervised) |
| Random Forest | Baseline supervisionado |
| XGBoost | Predição de falha (principal) |
| LSTM | Dependências temporais e RUL |
| Transformer | Fase experimental avançada |

---

## Estrutura do repositório

```text
industrial-predictive-maintenance/
│
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── simulator/
├── streaming/
├── ml/
├── api/
├── decision_engine/
├── infrastructure/
├── tests/
├── docs/
└── scripts/
```

---

## Roadmap

| Milestone | Descrição |
|---|---|
| 1 | Dataset — preparação do C-MAPSS e geração de labels RUL |
| 2 | ML Baseline — feature engineering, XGBoost, MLflow |
| 3 | Simulator — produtor Kafka a partir do dataset |
| 4 | Streaming — Kafka + Spark + Delta (Bronze/Silver/Gold) |
| 5 | Real-Time Inference — features + modelo + predictions em streaming |
| 6 | API — FastAPI + PostgreSQL |
| 7 | Dashboard — fleet overview, machine detail, alerts |
| 8 | Observability — Prometheus + Grafana |
| 9 | MLOps — Model Registry, versionamento, monitoring, retraining |
| 10 | Mining Edition — adaptação para equipamentos de mineração |

---

## Versões

| Versão | Foco |
|---|---|
| V1 | Machine Learning — C-MAPSS + XGBoost + MLflow |
| V2 | Data Engineering — Simulator + Kafka + Spark + Delta |
| V3 | Real-Time ML — inferência em streaming |
| V4 | Full Platform — pipeline completo end-to-end |
| V5 | Advanced Intelligence — LSTM, RUL, Drift, Retraining |
| V6 | Mining Edition — domínio de mineração |

---

## Como executar (desenvolvimento local)

```bash
git clone https://github.com/marcelinolufendo/industrial-predictive-maintenance.git
cd industrial-predictive-maintenance
cp .env.example .env
docker compose up
```

---

## Observabilidade

- **Infraestrutura** — CPU, RAM, Disk, container health
- **Pipeline** — Kafka lag, throughput, latência, batch duration
- **ML** — anomaly rate, failure probability distribution, data drift, model drift

---

## Princípios de arquitetura

1. **Streaming-first** — eventos tratados como fluxo contínuo
2. **Data quality first** — ML depende da qualidade dos dados
3. **Separation of concerns** — ingestão, processamento, ML e decisão são componentes separados
4. **Reproducibility** — modelos e experimentos reproduzíveis via MLflow
5. **Observability** — pipeline monitorável end-to-end
6. **Fault tolerance** — checkpoints Spark para recuperação
7. **Scalability** — Kafka partitions + Spark workers escaláveis horizontalmente
8. **Explainability** — previsões com feature importance e SHAP values
9. **Versioning** — dados, features e modelos versionados
10. **Domain adaptability** — arquitetura migrável de C-MAPSS para equipamentos reais

---

## Limitações

- C-MAPSS é um dataset experimental — resultados não representam desempenho industrial real
- Thresholds iniciais (anomaly score, failure probability) não são limites industriais validados
- RUL é uma estimativa, não uma garantia
- Validação industrial exige dados reais, conhecimento de domínio e testes em campo

---

## Licença

MIT
