# Industrial Predictive Maintenance & Real-Time Intelligence Platform

## 1. Visão geral

Este projeto propõe a construção de uma plataforma industrial de **manutenção preditiva em tempo real**, capaz de receber continuamente dados de sensores de equipamentos, processá-los através de streaming, gerar features temporais, executar modelos de Machine Learning e produzir decisões operacionais sobre o estado de cada máquina.

O sistema foi concebido para representar um ambiente industrial real, mesmo sem depender de sensores físicos. Para isso, um simulador em Python utiliza dados históricos, inicialmente o **NASA C-MAPSS**, e os publica no Apache Kafka como se fossem eventos produzidos por sensores reais.

A plataforma terá como objetivos principais:

1. Monitorar equipamentos continuamente.
2. Detectar comportamentos anormais.
3. Estimar o risco de falha.
4. Estimar Remaining Useful Life (RUL) em uma etapa avançada.
5. Armazenar dados históricos em um Data Lake.
6. Processar eventos em tempo real com Apache Spark.
7. Versionar e gerir modelos com MLflow.
8. Disponibilizar previsões através de uma API.
9. Apresentar estado e histórico das máquinas em dashboards.
10. Implementar observabilidade de infraestrutura, pipeline e Machine Learning.
11. Permitir adaptação posterior para equipamentos de mineração.

---

# 2. Objetivo geral

Construir uma plataforma de **Predictive Maintenance** que transforme telemetria de máquinas em informação operacional acionável.

Fluxo conceitual:

```text
Sensores
   ↓
Kafka
   ↓
Spark Structured Streaming
   ↓
Feature Engineering
   ↓
Machine Learning
   ↓
Prediction
   ↓
Decision Engine
   ↓
API / Dashboard / Alertas
```

A ideia central é sair de uma abordagem puramente histórica:

```text
Dataset → Treino → Modelo → Previsão
```

para uma arquitetura contínua:

```text
Sensor → Evento → Streaming → Feature → Modelo → Decisão → Ação
```

---

# 3. Problema de negócio

Equipamentos industriais apresentam sinais de degradação antes de uma falha.

Esses sinais podem aparecer através de alterações em:

- temperatura;
- vibração;
- RPM;
- corrente;
- tensão;
- pressão;
- vazão;
- horas de operação;
- consumo;
- frequência de eventos;
- tendência temporal dos sensores.

Um sistema tradicional pode esperar pela ocorrência de uma falha:

```text
Máquina
   ↓
Falha
   ↓
Paragem
   ↓
Manutenção
```

A proposta deste projeto é antecipar esse comportamento:

```text
Máquina
   ↓
Degradação
   ↓
Anomalia
   ↓
Aumento do risco
   ↓
Alerta
   ↓
Inspeção / manutenção
   ↓
Evitar ou reduzir impacto da falha
```

---

# 4. Casos de uso

## 4.1 Monitoramento de condição

Responder:

> Qual é o estado atual da máquina?

Estados possíveis:

```text
NORMAL
WARNING
CRITICAL
```

---

## 4.2 Detecção de anomalias

Responder:

> O comportamento atual da máquina está diferente do padrão esperado?

Exemplo:

```text
Temperatura normal: 65°C
Temperatura atual: 91°C

Vibração normal: 0.20
Vibração atual: 0.87

RPM normal: 1800
RPM atual: 1800
```

Resultado:

```text
ANOMALY SCORE = 0.91
STATUS = WARNING
```

Uma anomalia não significa necessariamente que uma falha irá acontecer. Ela significa que o comportamento observado está distante do padrão considerado normal.

---

## 4.3 Predição de falha

Responder:

> Qual é a probabilidade de a máquina falhar dentro de determinado horizonte?

Exemplo:

```text
Failure Probability = 0.87
Prediction Horizon = 24h
```

---

## 4.4 Remaining Useful Life

Responder:

> Quanto tempo ou quantos ciclos aproximadamente restam até uma condição de falha?

Exemplo:

```text
RUL = 35 ciclos
```

A previsão de RUL será tratada como uma capacidade avançada do projeto.

---

# 5. Anomalia, risco e falha

É importante separar os conceitos.

## Anomalia

Indica comportamento fora do padrão.

```text
Anomaly Score = 0.89
```

## Risco de falha

Indica probabilidade estimada de falha em determinado horizonte.

```text
Failure Probability = 0.81
```

## Falha

Representa uma condição de falha efetivamente identificada no dataset ou no sistema.

```text
Failure = 1
```

## RUL

Representa a estimativa de vida útil restante.

```text
RUL = 37 ciclos
```

Esses conceitos não devem ser tratados como equivalentes.

---

# 6. Domínio inicial

O projeto começará utilizando o **NASA C-MAPSS**, um conjunto de dados de degradação de motores turbofan.

O dataset é adequado para experimentos de:

- séries temporais;
- degradação;
- previsão de falhas;
- RUL;
- feature engineering;
- Machine Learning.

Entretanto, o C-MAPSS não representa diretamente uma fábrica ou mina com sensores IoT reais.

Por isso, será criado um **Sensor Simulator**.

---

# 7. Sensor Simulator

O simulador será responsável por transformar registros históricos em eventos temporais.

Arquitetura:

```text
NASA C-MAPSS
     ↓
Dataset Reader
     ↓
Preprocessor
     ↓
Sensor Simulator
     ↓
Kafka Producer
```

O simulador poderá controlar:

- velocidade de envio;
- máquina;
- timestamp;
- ciclo;
- sensores;
- atraso artificial;
- eventos fora de ordem;
- falhas;
- dados inválidos;
- ausência de sensores;
- variações de comportamento.

Exemplo de evento:

```json
{
  "machine_id": "M001",
  "timestamp": "2026-10-03T17:30:01.000Z",
  "cycle": 142,
  "temperature": 72.4,
  "vibration": 0.31,
  "rpm": 1820,
  "pressure": 4.2,
  "current": 81.4,
  "voltage": 380.2,
  "operating_hours": 1532.4
}
```

---

# 8. Arquitetura geral

```text
                           ┌─────────────────────┐
                           │   NASA C-MAPSS      │
                           │ Historical Dataset  │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │  Sensor Simulator   │
                           │       Python        │
                           └──────────┬──────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │       Kafka         │
                           │   sensor.telemetry  │
                           └──────────┬──────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────┐
                    │ Spark Structured Streaming      │
                    │                                 │
                    │ - validation                    │
                    │ - deduplication                 │
                    │ - watermark                     │
                    │ - window aggregation            │
                    │ - feature engineering           │
                    └───────────────┬─────────────────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
             Bronze             Silver               Gold
              Delta              Delta               Delta
                 │                  │                  │
                 │                  │                  ▼
                 │                  │            ML Features
                 │                  │                  │
                 │                  │         ┌────────┴────────┐
                 │                  │         ▼                 ▼
                 │                  │    Anomaly Model     Failure Model
                 │                  │         │                 │
                 │                  │         └────────┬────────┘
                 │                  │                  ▼
                 │                  │           Decision Engine
                 │                  │                  │
                 └──────────────────┴──────────────────┤
                                                       ▼
                                                   PostgreSQL
                                                       │
                                                       ▼
                                                     FastAPI
                                                       │
                                      ┌────────────────┼───────────────┐
                                      ▼                ▼               ▼
                                  Dashboard         Alerts          Clients
```

---

# 9. Stack tecnológica

## Dados

- NASA C-MAPSS
- Python
- Pandas / PyArrow quando necessário

## Streaming

- Apache Kafka
- Kafka Producer
- Kafka Consumer

## Processamento

- Apache Spark
- Spark Structured Streaming
- Spark SQL

## Data Lake

- Delta Lake
- Parquet
- MinIO como armazenamento S3-compatible em uma etapa de infraestrutura

## Machine Learning

- Scikit-learn
- XGBoost

## Deep Learning

- PyTorch
- LSTM
- Transformers para séries temporais em fase avançada

## MLOps

- MLflow
- MLflow Tracking
- MLflow Model Registry

## API

- FastAPI
- Pydantic

## Banco operacional

- PostgreSQL

## Observabilidade

- Prometheus
- Grafana
- Alertmanager
- eventualmente Loki

## Infraestrutura

- Docker
- Docker Compose

---

# 10. Arquitetura de dados

A plataforma seguirá inicialmente um modelo inspirado em arquitetura Medallion.

```text
RAW
 ↓
BRONZE
 ↓
SILVER
 ↓
GOLD
```

---

# 11. Bronze Layer

A Bronze representa os dados próximos da origem.

Objetivos:

- preservar dados recebidos;
- permitir auditoria;
- manter histórico;
- possibilitar reprocessamento;
- não destruir informação original.

Exemplo:

```text
bronze/
  telemetry/
    machine_id=M001/
      year=2026/
        month=10/
          day=03/
```

Schema conceitual:

```text
machine_id
timestamp
cycle
temperature
vibration
rpm
pressure
current
voltage
operating_hours
ingestion_timestamp
source
```

---

# 12. Silver Layer

A Silver contém dados tratados.

Processos:

```text
Bronze
 ↓
Schema validation
 ↓
Type casting
 ↓
Null handling
 ↓
Deduplication
 ↓
Watermark
 ↓
Data quality
 ↓
Silver
```

Exemplos de validações:

```text
temperature IS NOT NULL
rpm >= 0
pressure >= 0
machine_id IS NOT NULL
timestamp IS NOT NULL
```

---

# 13. Gold Layer

A Gold contém dados preparados para consumo analítico e ML.

Exemplo:

```text
machine_id
timestamp

temperature_mean_30s
temperature_max_30s
temperature_std_30s
temperature_slope_30s

vibration_mean_30s
vibration_max_30s
vibration_std_30s
vibration_slope_30s

rpm_mean_30s
rpm_std_30s

pressure_mean_30s
pressure_std_30s

current_mean_30s
current_std_30s

operating_hours
cycle

anomaly_score
failure_probability
rul
status
```

---

# 14. Processamento temporal

O projeto não deverá depender apenas do valor instantâneo de um sensor.

Exemplo:

```text
Temperatura:

65
66
68
70
74
79
84
89
```

O valor atual é importante:

```text
89°C
```

Mas a tendência também é importante:

```text
65 → 89°C
```

Portanto, serão utilizadas janelas temporais.

Exemplo:

```text
30 segundos
60 segundos
5 minutos
```

---

# 15. Window Functions

Features possíveis:

```text
avg()
max()
min()
stddev()
```

E features derivadas:

```text
slope
delta
rate_of_change
rolling_mean
rolling_std
```

Exemplo:

```text
temperature_mean_30s
temperature_max_30s
temperature_std_30s
temperature_delta_30s
temperature_slope_30s
```

---

# 16. Watermark

O streaming deverá considerar eventos atrasados.

Exemplo:

```text
10:00:01
10:00:02
10:00:05
10:00:03
```

O evento de 10:00:03 chegou atrasado.

O watermark permite ao Spark controlar quanto tempo deve esperar por eventos atrasados antes de considerar uma janela suficientemente completa.

Configuração conceitual:

```text
watermark = 30 seconds
window = 30 seconds
```

Os valores finais serão definidos durante os testes de latência e volume.

---

# 17. Deduplicação

Eventos duplicados não devem produzir duas vezes a mesma informação.

Uma chave possível:

```text
machine_id + timestamp + cycle
```

Ou um identificador de evento:

```text
event_id
```

Exemplo:

```json
{
  "event_id": "M001-142-20261003173001"
}
```

---

# 18. Data Quality

A plataforma deverá validar:

### Identidade

```text
machine_id não pode ser NULL
```

### Timestamp

```text
timestamp válido
```

### Sensores

```text
temperature dentro de limites plausíveis
rpm >= 0
pressure >= 0
```

### Integridade

```text
event_id único
```

### Schema

O produtor e o consumidor devem respeitar um contrato de dados.

---

# 19. Kafka

Kafka será a camada de ingestão de eventos.

Fluxo:

```text
Sensor Simulator
      ↓
Kafka Producer
      ↓
Topic
      ↓
Spark Streaming
```

Topic inicial:

```text
machine.telemetry
```

Outros tópicos possíveis:

```text
machine.predictions
machine.alerts
machine.events
```

---

# 20. Particionamento Kafka

A chave recomendada será:

```text
machine_id
```

Isso permite manter a ordem dos eventos de uma determinada máquina dentro da sua partição.

Exemplo:

```text
Partition 0 → M001
Partition 1 → M002
Partition 2 → M003
```

A estratégia final dependerá da quantidade de máquinas e throughput.

---

# 21. Spark Structured Streaming

O Spark será responsável por:

1. Ler Kafka.
2. Desserializar eventos.
3. Validar schema.
4. Fazer casting.
5. Remover duplicados.
6. Aplicar watermark.
7. Criar janelas.
8. Calcular features.
9. Executar inferência.
10. Persistir resultados.

Fluxo:

```text
Kafka
 ↓
readStream
 ↓
from_json
 ↓
validation
 ↓
watermark
 ↓
window
 ↓
feature engineering
 ↓
ML inference
 ↓
writeStream
```

---

# 22. Machine Learning

O projeto terá inicialmente três famílias de modelos.

## 22.1 Isolation Forest

Utilizado para detecção de anomalias.

Entrada:

```text
temperature
vibration
rpm
pressure
current
```

Saída:

```text
anomaly_score
```

---

## 22.2 Random Forest

Será utilizado como baseline supervisionado quando houver labels.

Exemplo:

```text
Failure = 0
Failure = 1
```

Objetivo:

```text
P(Failure)
```

---

## 22.3 XGBoost

Será o principal candidato para o modelo tabular supervisionado.

Features:

```text
temperature_mean
temperature_std
temperature_slope
vibration_mean
vibration_std
pressure_mean
rpm_mean
...
```

Saída:

```text
failure_probability
```

---

# 23. Deep Learning

Após estabelecer uma baseline robusta, será testado um modelo LSTM.

Estrutura conceitual:

```text
t-10
t-9
t-8
t-7
t-6
t-5
t-4
t-3
t-2
t-1
  ↓
 LSTM
  ↓
Prediction
```

O LSTM será utilizado para explorar dependências temporais que modelos tabulares podem não capturar diretamente.

---

# 24. Transformer

O Transformer para séries temporais será tratado como uma etapa experimental avançada.

Objetivo:

- lidar com sequências maiores;
- aprender relações entre múltiplos sensores;
- comparar desempenho com LSTM;
- estudar custo computacional;
- avaliar latência de inferência.

Não será obrigatório para a primeira versão.

---

# 25. RUL

RUL significa:

> Remaining Useful Life

Representa a vida útil estimada restante.

Exemplo:

```text
Cycle = 120
Estimated Failure Cycle = 155

RUL = 35
```

O pipeline pode calcular labels de treinamento como:

```text
RUL = failure_cycle - current_cycle
```

O modelo aprenderá a estimar:

```text
RUL ≈ 35
```

---

# 26. Estratégia de RUL

Primeira abordagem:

```text
C-MAPSS
 ↓
RUL Label
 ↓
Feature Engineering
 ↓
XGBoost Regressor
 ↓
RUL Prediction
```

Depois:

```text
Sequence
 ↓
LSTM
 ↓
RUL
```

E, posteriormente:

```text
Sequence
 ↓
Transformer
 ↓
RUL
```

---

# 27. Decision Engine

O modelo não deverá ser responsável por toda a lógica operacional.

Exemplo:

```text
Anomaly Score = 0.92
Failure Probability = 0.84
RUL = 17
```

O Decision Engine poderá produzir:

```json
{
  "status": "CRITICAL",
  "reasons": [
    "high_anomaly_score",
    "high_failure_probability",
    "low_rul"
  ]
}
```

---

# 28. Estados operacionais

Exemplo inicial:

## NORMAL

```text
anomaly_score < 0.50
failure_probability < 0.30
```

## WARNING

```text
anomaly_score >= 0.50
ou
failure_probability >= 0.30
```

## CRITICAL

```text
anomaly_score >= 0.80
ou
failure_probability >= 0.70
ou
RUL abaixo de determinado limite
```

Esses valores são apenas parâmetros iniciais. Não devem ser tratados como limites industriais reais sem validação de domínio.

---

# 29. Modelo de decisão

Exemplo:

```text
             Prediction
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
 Anomaly Score  Failure    RUL
               Probability
       │          │          │
       └──────────┼──────────┘
                  ▼
           Decision Engine
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
     NORMAL     WARNING    CRITICAL
```

---

# 30. Alertas

Quando uma máquina atingir uma condição crítica:

```text
Machine M001
Status: CRITICAL
Failure Probability: 87%
RUL: 12 cycles
```

poderá gerar:

```text
Kafka Alert Event
        ↓
Alert Service
        ↓
Webhook / Email / Dashboard
```

Alertas poderão conter:

- máquina;
- timestamp;
- nível;
- score;
- motivo;
- RUL;
- features relevantes;
- modelo utilizado.

---

# 31. FastAPI

A API disponibilizará os dados para aplicações externas.

Endpoints possíveis:

```text
GET /machines
GET /machines/{machine_id}
GET /machines/{machine_id}/telemetry
GET /machines/{machine_id}/predictions
GET /machines/{machine_id}/alerts
GET /machines/{machine_id}/health
GET /machines/{machine_id}/rul
```

---

# 32. Endpoint de previsão

Exemplo:

```text
POST /predict
```

Entrada:

```json
{
  "machine_id": "M001",
  "temperature": 88.2,
  "vibration": 0.72,
  "rpm": 1790,
  "pressure": 3.4
}
```

Resposta:

```json
{
  "machine_id": "M001",
  "anomaly_score": 0.87,
  "failure_probability": 0.81,
  "rul": 37,
  "status": "WARNING"
}
```

---

# 33. PostgreSQL

PostgreSQL será utilizado para dados operacionais e consultas rápidas da API.

Não será o Data Lake principal.

Exemplos de tabelas:

```text
machines
predictions
alerts
model_versions
machine_status
```

---

# 34. Data Lake

O Data Lake será responsável pelo histórico.

Estrutura conceitual:

```text
data/
├── bronze/
│   └── telemetry/
│
├── silver/
│   └── telemetry/
│
├── gold/
│   ├── features/
│   ├── predictions/
│   └── machine_health/
│
└── models/
```

---

# 35. Delta Lake

Delta será utilizado para fornecer capacidades como:

- transações;
- schema enforcement;
- histórico;
- evolução de schema;
- operações de leitura/escrita mais controladas;
- suporte adequado ao processamento analítico.

---

# 36. MinIO

MinIO poderá atuar como object storage S3-compatible.

Exemplo:

```text
Spark
  ↓
S3A
  ↓
MinIO
  ↓
Delta / Parquet
```

Estrutura:

```text
s3://predictive-maintenance/
```

---

# 37. MLflow

MLflow será utilizado para gerir o ciclo de vida dos modelos.

Componentes:

```text
MLflow Tracking
MLflow Artifacts
MLflow Model Registry
```

Durante o treino:

```text
Dataset
 ↓
Training
 ↓
MLflow Experiment
 ↓
Metrics
 ↓
Model
 ↓
Registry
```

---

# 38. Métricas de ML

Para classificação:

```text
Accuracy
Precision
Recall
F1
ROC-AUC
PR-AUC
```

Para RUL:

```text
MAE
RMSE
R²
```

Para anomalias:

```text
Precision
Recall
False Positive Rate
False Negative Rate
```

Em manutenção preditiva, falsos positivos e falsos negativos devem ser analisados separadamente, pois têm impactos operacionais diferentes.

---

# 39. Model Registry

Exemplo:

```text
predictive-maintenance-model
```

Versões:

```text
v1
v2
v3
```

Ciclo:

```text
Training
   ↓
Validation
   ↓
Candidate
   ↓
Production
```

A aplicação deverá registrar qual versão do modelo gerou cada previsão.

---

# 40. Reprodutibilidade

Cada prediction deve poder ser associada a:

```text
model_name
model_version
prediction_timestamp
feature_version
dataset_version
```

Exemplo:

```json
{
  "model_name": "failure-predictor",
  "model_version": "v3",
  "feature_version": "v2",
  "prediction_timestamp": "2026-10-03T17:40:00Z"
}
```

---

# 41. Observabilidade

A plataforma deverá ser observável em três dimensões.

## Infraestrutura

```text
CPU
RAM
Disk
Network
Container health
```

## Pipeline

```text
Kafka throughput
Kafka lag
records processed
processing latency
batch duration
failed batches
watermark
```

## Machine Learning

```text
prediction count
anomaly rate
failure probability distribution
RUL distribution
model latency
data drift
prediction drift
```

---

# 42. Prometheus

Métricas importantes:

```text
kafka_consumer_lag
streaming_records_processed
streaming_processing_latency
prediction_latency
prediction_total
alerts_total
```

---

# 43. Grafana

Dashboards propostos:

## Dashboard 1 — Fleet Overview

```text
Machines monitored
Normal
Warning
Critical
Active alerts
```

## Dashboard 2 — Machine Health

```text
Temperature
Vibration
RPM
Pressure
Current
Anomaly Score
Failure Probability
RUL
```

## Dashboard 3 — Streaming

```text
Throughput
Latency
Kafka Lag
Batch Duration
Errors
```

## Dashboard 4 — ML

```text
Predictions
Anomalies
Failure Probability
RUL
Model Version
Drift
```

---

# 44. Dashboard operacional

Exemplo:

```text
╔══════════════════════════════════════════════╗
║       PREDICTIVE MAINTENANCE PLATFORM       ║
╠══════════════════════════════════════════════╣
║ Machines monitored                  50       ║
║ Normal                              42       ║
║ Warning                              5       ║
║ Critical                             3       ║
║ Active Alerts                        8       ║
╠══════════════════════════════════════════════╣
║ Machine    Status      Risk       RUL       ║
║ M-001      NORMAL       12%      142        ║
║ M-002      WARNING      57%       57        ║
║ M-003      CRITICAL     91%       12        ║
╚══════════════════════════════════════════════╝
```

---

# 45. Página de detalhe da máquina

```text
MACHINE M-003
──────────────────────────────

Status: CRITICAL

Failure Probability
██████████████████░░ 91%

RUL
12 cycles

Anomaly Score
0.94

Temperature
65 → 70 → 76 → 84 → 91°C

Vibration
0.20 → 0.31 → 0.44 → 0.67 → 0.87

Pressure
4.4 → 4.2 → 4.0 → 3.7 → 3.2
```

---

# 46. Adaptabilidade para mineração

Depois da validação com C-MAPSS, o projeto poderá ser adaptado para mineração.

Equipamentos possíveis:

- britadores;
- moinhos;
- bombas;
- correias transportadoras;
- ventiladores;
- compressores;
- motores;
- peneiras vibratórias.

---

# 47. Sensores para mineração

## Britador

```text
Vibração
Temperatura
RPM
Corrente
Pressão hidráulica
```

## Bomba

```text
Pressão
Vazão
Temperatura
Vibração
RPM
Corrente
```

## Correia transportadora

```text
Velocidade
Corrente
Vibração
Temperatura
Tensão
Carga
```

---

# 48. Arquitetura de mineração

```text
                 MINING EQUIPMENT
                       │
       ┌───────────────┼────────────────┐
       ▼               ▼                ▼
   Crusher           Pump           Conveyor
       │               │                │
       └───────────────┼────────────────┘
                       ▼
                 Sensor Events
                       │
                       ▼
                     Kafka
                       │
                       ▼
                Spark Streaming
                       │
                       ▼
                 Feature Layer
                       │
              ┌────────┴────────┐
              ▼                 ▼
        Anomaly Model      Failure Model
              │                 │
              └────────┬────────┘
                       ▼
                 Decision Engine
                       │
                       ▼
                    Alerts
```

---

# 49. Segurança

A API deverá considerar:

- autenticação;
- autorização;
- secrets via environment variables;
- TLS quando implantada fora do ambiente local;
- controle de acesso aos dashboards;
- segregação de ambientes;
- proteção de endpoints administrativos.

Ambientes:

```text
DEV
QUA
PRD
```

---

# 50. Configuração

As configurações não deverão ser hardcoded.

Exemplo:

```text
KAFKA_BOOTSTRAP_SERVERS
KAFKA_TOPIC_TELEMETRY
MINIO_ENDPOINT
MINIO_ACCESS_KEY
MINIO_SECRET_KEY
POSTGRES_HOST
POSTGRES_PORT
MLFLOW_TRACKING_URI
MODEL_NAME
WATERMARK_DELAY
WINDOW_DURATION
```

---

# 51. Estrutura de repositório

Estrutura sugerida:

```text
industrial-predictive-maintenance/
│
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── simulator/
│   ├── producers/
│   │   └── telemetry_producer.py
│   ├── loaders/
│   │   └── cmapss_loader.py
│   └── config/
│
├── streaming/
│   ├── jobs/
│   │   ├── bronze_ingestion.py
│   │   ├── silver_processing.py
│   │   ├── feature_engineering.py
│   │   └── inference.py
│   ├── schemas/
│   └── config/
│
├── ml/
│   ├── training/
│   │   ├── train_anomaly.py
│   │   ├── train_failure.py
│   │   └── train_rul.py
│   ├── inference/
│   ├── features/
│   ├── evaluation/
│   └── notebooks/
│
├── api/
│   ├── main.py
│   ├── routes/
│   ├── services/
│   ├── schemas/
│   └── repositories/
│
├── decision_engine/
│   ├── rules.py
│   ├── scoring.py
│   └── alerts.py
│
├── infrastructure/
│   ├── kafka/
│   ├── spark/
│   ├── minio/
│   ├── postgres/
│   ├── mlflow/
│   ├── prometheus/
│   └── grafana/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── streaming/
│
├── docs/
│   ├── architecture.md
│   ├── data-model.md
│   ├── ml.md
│   ├── streaming.md
│   ├── observability.md
│   ├── deployment.md
│   └── runbook.md
│
└── scripts/
    ├── bootstrap.sh
    ├── train_models.sh
    └── start_simulator.sh
```

---

# 52. Docker Compose

Serviços iniciais:

```text
kafka
kafka-ui
spark-master
spark-worker
minio
postgres
mlflow
prometheus
grafana
api
```

O projeto poderá começar com menos serviços e crescer gradualmente.

---

# 53. Desenvolvimento local

Fluxo:

```text
git clone
    ↓
configure .env
    ↓
docker compose up
    ↓
create Kafka topics
    ↓
load C-MAPSS
    ↓
train model
    ↓
register model
    ↓
start Spark
    ↓
start simulator
    ↓
open dashboard
```

---

# 54. Testes

## Unit Tests

Testar:

- feature calculations;
- validation;
- decision rules;
- data transformations.

## Integration Tests

Testar:

```text
Kafka → Spark → Delta
```

## ML Tests

Testar:

- schema;
- feature compatibility;
- model loading;
- prediction output;
- model metrics.

## End-to-End

Testar:

```text
Simulator
 ↓
Kafka
 ↓
Spark
 ↓
ML
 ↓
PostgreSQL
 ↓
API
 ↓
Dashboard
```

---

# 55. Data Contract

O evento de telemetria deverá possuir um contrato.

Exemplo:

```json
{
  "event_id": "string",
  "machine_id": "string",
  "timestamp": "datetime",
  "cycle": "integer",
  "temperature": "float",
  "vibration": "float",
  "rpm": "float",
  "pressure": "float",
  "current": "float",
  "voltage": "float",
  "operating_hours": "float"
}
```

O contrato deverá evoluir de forma controlada.

---

# 56. Performance

A plataforma deverá medir:

```text
events/sec
records/sec
latency
batch duration
Kafka lag
CPU
memory
model inference latency
```

O objetivo inicial não é atingir um número industrial específico.

Primeiro deve ser estabelecida uma baseline.

Depois serão realizados testes de carga.

---

# 57. Teste de carga

O simulador poderá produzir:

```text
100 events/sec
1,000 events/sec
5,000 events/sec
10,000 events/sec
```

Será analisado:

```text
Throughput
Latency
Kafka Lag
Spark Processing Time
CPU
Memory
```

---

# 58. Escalabilidade

A arquitetura deverá permitir aumentar:

```text
Kafka partitions
        +
Spark workers
        +
processing parallelism
```

Exemplo:

```text
100 machines
   ↓
10 Kafka partitions
   ↓
3 Spark workers
```

Depois:

```text
10,000 machines
   ↓
mais partitions
   ↓
mais workers
```

Os valores finais dependerão dos testes.

---

# 59. Backpressure

Se os produtores enviarem dados mais rapidamente do que o pipeline consegue processar:

```text
Producer
   ↓
Kafka
   ↓
Lag ↑
   ↓
Spark
```

O Kafka deverá absorver temporariamente o fluxo enquanto o processamento é escalado.

Kafka lag será uma métrica importante.

---

# 60. Fault tolerance

O sistema deverá considerar:

- reinício de Spark;
- reinício de Kafka;
- falha do produtor;
- falha da API;
- falha do MLflow;
- perda temporária de conexão com MinIO;
- processamento duplicado;
- eventos atrasados.

Checkpoints do Spark serão utilizados para permitir recuperação do streaming.

---

# 61. Idempotência

Operações de persistência deverão evitar duplicação quando possível.

O desenho deverá considerar:

```text
event_id
machine_id
timestamp
batch_id
```

e estratégias apropriadas de escrita.

---

# 62. Model Drift

Com o tempo, o comportamento das máquinas pode mudar.

Exemplo:

```text
Treino:
temperature média = 65°C

Produção:
temperature média = 75°C
```

Isso pode indicar alteração na distribuição dos dados.

O sistema poderá monitorar:

```text
feature drift
prediction drift
```

---

# 63. Data Drift

Exemplo:

```text
Training distribution
        ↓
temperature = 60-70°C

Production distribution
        ↓
temperature = 70-90°C
```

O sistema deverá registrar essa diferença e gerar um indicador de drift.

---

# 64. Model Monitoring

Dashboard:

```text
MODEL MONITORING

Model: failure-predictor
Version: v3

Predictions: 1,240,302
Average latency: 18ms
Anomaly rate: 8.4%
Average failure probability: 0.23
Drift score: 0.12
```

---

# 65. Ciclo de vida do modelo

```text
Data
 ↓
Training
 ↓
Evaluation
 ↓
Experiment
 ↓
Model Registry
 ↓
Candidate
 ↓
Production
 ↓
Monitoring
 ↓
Retraining
```

---

# 66. Retreinamento

Inicialmente poderá ser manual.

Depois poderá ser automatizado.

Exemplo:

```text
New historical data
       ↓
Quality check
       ↓
Retraining
       ↓
Evaluation
       ↓
Compare with Production
       ↓
Register new version
```

A promoção automática para produção deverá depender de critérios de validação bem definidos.

---

# 67. Explainability

Para modelos tabulares como XGBoost, será interessante apresentar:

- feature importance;
- SHAP values;
- principais fatores associados à previsão.

Exemplo:

```text
Failure Probability = 87%

Contributing factors:

Vibration slope       +0.31
Temperature slope     +0.24
Pressure decrease     +0.18
Current increase      +0.11
```

Isso torna a previsão mais interpretável para operadores.

---

# 68. Decisão explicável

O dashboard poderá apresentar:

```text
⚠️ WARNING

Machine M-002

Reason:
- vibration increasing rapidly
- temperature above baseline
- pressure decreasing

Failure Probability:
57%

RUL:
57 cycles
```

---

# 69. Roadmap

## Milestone 1 — Dataset

- baixar/preparar C-MAPSS;
- entender schema;
- criar dataset limpo;
- gerar RUL.

## Milestone 2 — ML Baseline

- feature engineering;
- Random Forest;
- XGBoost;
- avaliação;
- MLflow.

## Milestone 3 — Simulator

- ler dataset;
- simular timestamp;
- enviar eventos Kafka.

## Milestone 4 — Streaming

- Kafka;
- Spark;
- Bronze;
- Silver;
- Gold.

## Milestone 5 — Real-Time Inference

- carregar modelo;
- gerar features;
- executar inferência;
- gravar predictions.

## Milestone 6 — API

- FastAPI;
- endpoints;
- PostgreSQL.

## Milestone 7 — Dashboard

- fleet overview;
- machine detail;
- alerts;
- RUL.

## Milestone 8 — Observability

- Prometheus;
- Grafana;
- Kafka metrics;
- Spark metrics;
- ML metrics.

## Milestone 9 — MLOps

- Model Registry;
- versionamento;
- deployment;
- monitoring;
- retraining.

## Milestone 10 — Mining Edition

- redefinir sensores;
- adaptar equipamentos;
- adaptar regras;
- criar simulador de mineração;
- dashboard de equipamentos mineiros.

---

# 70. V1 — Machine Learning

Arquitetura:

```text
C-MAPSS
 ↓
Feature Engineering
 ↓
XGBoost
 ↓
Failure Prediction
```

Entrega:

```text
model.pkl
metrics.json
MLflow experiment
```

---

# 71. V2 — Data Engineering

```text
C-MAPSS
 ↓
Simulator
 ↓
Kafka
 ↓
Spark
 ↓
Delta
```

Entrega:

- streaming funcional;
- Data Lake;
- Bronze/Silver/Gold.

---

# 72. V3 — Real-Time ML

```text
Kafka
 ↓
Spark
 ↓
Features
 ↓
ML
 ↓
Prediction
```

Entrega:

```text
machine_id
anomaly_score
failure_probability
```

---

# 73. V4 — Full Platform

```text
Sensor Simulator
       ↓
     Kafka
       ↓
     Spark
       ↓
   Data Lake
       ↓
Feature Engineering
       ↓
     MLflow
       ↓
      Model
       ↓
Decision Engine
       ↓
    FastAPI
       ↓
 Dashboard
       ↓
   Alerts
```

---

# 74. V5 — Advanced Intelligence

Adicionar:

```text
LSTM
RUL
Transformers
SHAP
Data Drift
Model Drift
Automated Retraining
```

---

# 75. V6 — Mining

Adaptar o domínio:

```text
Aircraft Engine
       ↓
Mining Equipment
```

Equipamentos:

```text
Crusher
Mill
Pump
Conveyor
Compressor
Motor
```

---

# 76. Critérios de sucesso

O projeto será considerado funcional quando conseguir:

### Ingestão

```text
Simulator → Kafka
```

### Streaming

```text
Kafka → Spark
```

### Data Lake

```text
Spark → Delta
```

### ML

```text
Features → Model → Prediction
```

### Decision Engine

```text
Prediction → Status
```

### API

```text
Prediction → FastAPI
```

### Dashboard

```text
API/DB → Dashboard
```

### Observabilidade

```text
Pipeline → Metrics → Grafana
```

### MLOps

```text
Training → MLflow → Registry → Production
```

---

# 77. Resultado final esperado

O sistema deverá permitir abrir o dashboard e visualizar:

```text
====================================================
        INDUSTRIAL PREDICTIVE MAINTENANCE
====================================================

Machines monitored: 50

NORMAL       42
WARNING       5
CRITICAL      3

Active alerts: 8

----------------------------------------------------

Machine     Status       Risk       RUL
M-001       NORMAL        8%       142
M-002       WARNING      57%        57
M-003       CRITICAL     91%        12

----------------------------------------------------

Streaming

Events/sec              4,821
Kafka Lag                   12
Processing latency        1.7s

----------------------------------------------------

ML

Model                    XGBoost
Version                  v3
Predictions              1,240,302
Anomaly rate             7.4%
```

Ao abrir M-003:

```text
MACHINE M-003
====================================================

STATUS
CRITICAL

Failure Probability
91%

Anomaly Score
0.94

Estimated RUL
12 cycles

----------------------------------------------------

TEMPERATURE
65 → 68 → 72 → 79 → 84 → 91°C

VIBRATION
0.20 → 0.24 → 0.31 → 0.48 → 0.67 → 0.87

PRESSURE
4.5 → 4.4 → 4.2 → 3.9 → 3.6 → 3.2

----------------------------------------------------

Main factors

Vibration increase
Temperature increase
Pressure decrease

----------------------------------------------------

Recommended action

INSPECTION REQUIRED
```

---

# 78. Princípios de arquitetura

O projeto seguirá os seguintes princípios:

1. **Streaming-first** — eventos devem ser tratados como fluxo.
2. **Data quality first** — ML depende da qualidade dos dados.
3. **Separation of concerns** — ingestão, processamento, ML e decisão serão componentes separados.
4. **Reproducibility** — modelos e experimentos devem ser reproduzíveis.
5. **Observability** — o pipeline deve ser monitorável.
6. **Fault tolerance** — falhas de componentes não devem destruir o histórico.
7. **Scalability** — Kafka e Spark devem permitir crescimento horizontal.
8. **Explainability** — previsões importantes devem possuir contexto.
9. **Versioning** — dados, features e modelos devem possuir versões quando necessário.
10. **Domain adaptability** — o sistema deve poder migrar de C-MAPSS para equipamentos reais ou simulados de mineração.

---

# 79. Limitações

O projeto deve deixar explícito que:

- C-MAPSS é um dataset experimental;
- os sensores adicionais de temperatura, pressão, corrente etc. podem ser simulados;
- os thresholds iniciais não representam limites industriais reais;
- RUL é uma estimativa e não uma garantia de falha;
- resultados do dataset não devem ser interpretados diretamente como desempenho em uma mina ou fábrica real;
- validação industrial exigiria dados reais, conhecimento de domínio e testes em campo.

---

# 80. Evolução para ambiente real

Quando existirem sensores reais, a camada:

```text
Sensor Simulator
```

poderá ser substituída por:

```text
PLC / IoT Gateway / OPC-UA / MQTT / Edge Device
```

Mantendo grande parte da arquitetura:

```text
Real Sensors
    ↓
Gateway
    ↓
Kafka
    ↓
Spark
    ↓
Data Lake
    ↓
ML
    ↓
Decision Engine
    ↓
Dashboard
```

Isso é uma característica importante da arquitetura: o simulador serve como substituto da fonte real, não como parte obrigatória do sistema final.

---

# 81. Visão de longo prazo

A plataforma pode evoluir para:

```text
Industrial Data Platform
        │
        ├── Real-Time Telemetry
        ├── Predictive Maintenance
        ├── Anomaly Detection
        ├── Failure Prediction
        ├── RUL
        ├── Asset Monitoring
        ├── ML Platform
        ├── Model Registry
        ├── Alerting
        └── Observability
```

Posteriormente:

```text
Mining Intelligence Platform
```

com suporte a múltiplos tipos de equipamento.

---

# 82. Resumo executivo

O projeto consiste na construção de uma plataforma de inteligência industrial orientada a eventos.

A arquitetura combina:

```text
Python
Kafka
Spark
Delta Lake
PostgreSQL
XGBoost
MLflow
FastAPI
Grafana
Prometheus
Docker
```

O sistema recebe telemetria continuamente, processa dados temporais, cria features, executa modelos de Machine Learning, calcula anomalias, risco de falha e RUL, aplica uma camada de decisão e disponibiliza os resultados através de APIs, dashboards e alertas.

A primeira fonte de dados será o NASA C-MAPSS, reproduzida através de um simulador de sensores.

A arquitetura será posteriormente adaptável para equipamentos industriais reais e, em particular, para equipamentos de mineração como:

```text
Britadores
Moinhos
Bombas
Correias
Compressores
Motores
```

O projeto pretende demonstrar, em uma única solução, competências de:

```text
Data Engineering
        +
Real-Time Streaming
        +
Apache Spark
        +
Apache Kafka
        +
Data Lake
        +
Machine Learning
        +
MLOps
        +
Model Monitoring
        +
API Engineering
        +
Observability
        +
Industrial Intelligence
```

O objetivo final não é apenas produzir uma previsão de Machine Learning, mas construir uma plataforma capaz de transformar dados de equipamentos em informação operacional em tempo real.
