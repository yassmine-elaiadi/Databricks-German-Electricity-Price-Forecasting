# Databricks-German-Electricity-Price-Forecasting

| Layer | Contents |
| --- | --- |
| **Bronze** | Raw files and tables exactly as received from the APIs |
| **Silver** | Cleaned data: correct types, consistent time zone, duplicates removed, sources joined on time |
| **Gold** | Feature table for the model: lagged prices, calendar features, weather and generation features |
 
---
 
## How success is measured
 
A model without a baseline proves nothing, so every model is compared against two **naive baselines**:
 
| Baseline | Rule |
| --- | --- |
| Same hour yesterday | Tomorrow's price at 14:00 = today's price at 14:00 |
| Same hour last week | Tomorrow's price at 14:00 = the price at 14:00 seven days earlier |
 
**Metric:** MAE (mean absolute error) in €/MWh.
**Success:** the model's MAE is clearly lower than both baselines.
 
---
 
## Design rules
 
- **No data leakage.** The model only uses data that would really be available at forecast time: weather *forecasts* (not tomorrow's actual weather) and prices only up to the forecast day.
- **Time resolution.** Since autumn 2025 the European day-ahead market trades in 15-minute periods. The project checks what SMARD delivers and decides between hourly and 15-minute forecasts.
---
 
## Deliverables
 
| Deliverable | What it shows |
| --- | --- |
| Bronze / Silver / Gold tables in Unity Catalog | Data engineering: ingestion, cleaning, features |
| Model tracked in MLflow | ML: experiments, metrics, model registry |
| Scheduled Databricks Job | Production thinking: the pipeline runs daily without manual steps |
| AI/BI dashboard | Forecast vs. actual, error over time, price drivers |
 
---
 
## Tech stack
 
- **Databricks Free Edition**: Serverless compute, Unity Catalog, Delta Lake, MLflow, Jobs, AI/BI dashboards
- **Python 3.12** and **PySpark**
- **Databricks Connect** and the **Databricks extension for VS Code** for local development
- **uv** for the Python environment
---
 
## Project status
 
| Phase | Status |
| --- | --- |
| 0 — Setup | 🟡 In progress |
| 1 — Bronze (ingestion) | ⚪ Not started |
| 2 — Silver (cleaning) | ⚪ Not started |
| 3 — Gold (features) | ⚪ Not started |
| 4 — ML with MLflow | ⚪ Not started |
| 5 — Predictions, Job, dashboard | ⚪ Not started |
| 6 — Polish and publish | ⚪ Not started |
 
---
 
## Out of scope (possible version 2)
 
- Gas and CO₂ prices as extra features
- Deep learning models
- Deployment on Azure
---
 
## Run it yourself
 
Setup instructions will be added once the pipeline is in place.
 