# Databricks-German-Electricity-Price-Forecasting
 
Forecasting the **German day-ahead electricity price** (bidding zone DE-LU, hourly) on Databricks: a medallion lakehouse built on public SMARD market data (Bundesnetzagentur), a model tracked and registered with MLflow, and a daily job feeding an AI/BI dashboard.
 
| Layer | Contents | Table(s) |
| --- | --- | --- |
| **Bronze** | Raw weekly JSON files exactly as received from the SMARD API (5 series: price, load, wind onshore, wind offshore, solar), plus one Delta table built from them | Volume `bronze.raw_files`, `bronze.smard_raw` |
| **Silver** | Cleaned hourly data: UTC key + Berlin time, one column per series, starts at the DE-LU market split (1 Oct 2018), rows without a price removed, 4 single-hour load gaps filled | `silver.smard_hourly` (70,608 rows, no missing hours) |
| **Gold** | Feature table for the model: calendar features, lagged prices, lagged load / wind / solar | `gold.price_features_hourly` (70,440 rows, 11 features, 0 NULLs) |
 
All tables live in the Unity Catalog catalog `energy_lakehouse`.
 
---
 
## How success is measured
 
A model without a baseline proves nothing, so every model is compared against two **naive baselines**:
 
| Baseline | Rule |
| --- | --- |
| Same hour yesterday | Tomorrow's price at 14:00 = today's price at 14:00 |
| Same hour last week | Tomorrow's price at 14:00 = the price at 14:00 seven days earlier |
 
**Metric:** MAE (mean absolute error) in €/MWh.
**Split:** by time, never random. Train = Oct 2018 – Sep 2025, test = **1 Oct 2025 – Oct 2026** (~1 year, all seasons, 9,240 hours).
**Success:** the model's MAE is clearly lower than both baselines.
 
### Results (test period)
 
| Model | MAE (€/MWh) | vs best baseline |
| --- | --- | --- |
| Baseline: same hour last week | 38.55 | — |
| Baseline: same hour yesterday | 30.26 | — |
| Linear Regression | 27.28 | −10% |
| **HistGradientBoosting** | **27.01** | **−11%** |
 
The winner is registered in Unity Catalog as **`energy_lakehouse.gold.price_forecaster`** (version 1, alias `@champion`) with an input/output signature.
 
The gap between the two models is small (0.27 €/MWh), so the **features are the limit, not the model**. The next improvements are better features (public holidays, SMARD forecasts of load / wind / solar), not fancier algorithms.
 
---
 
## Design rules
 
- **No data leakage.** The forecast is made at the day-ahead auction (day D-1, 12:00). The model only uses what is known at that moment:
  - **Prices** are lagged by **≥ 24 h** (all of D-1's prices are known at the auction).
  - **Load, wind and solar** are measured *after* the hour, so they are lagged by **≥ 48 h**.
  - **Calendar features** (hour, weekday, month, weekend) never leak; they are computed from German local time.
- **Time resolution: hourly.** Since 1 Oct 2025 the day-ahead market trades in 15-minute periods, but only hourly data gives 8 consistent years of history. SMARD's hourly price is the average of the four quarter-hours. 15-minute forecasts are a v2 idea.
- **Time zones:** everything is keyed on **UTC**. Berlin time repeats an hour at the October clock change, so it can't be a key.
- **Reproducible runs:** every training run is logged in MLflow (parameters, metric, model, Git commit), with a fixed `random_state`.
---
 
## Deliverables
 
| Deliverable | What it shows | Status |
| --- | --- | --- |
| Bronze / Silver / Gold tables in Unity Catalog | Data engineering: ingestion, cleaning, features | ✅ |
| Model tracked in MLflow + registered in Unity Catalog | ML: experiments, metrics, model registry, aliases | ✅ |
| Scheduled Databricks Job | Production thinking: the pipeline runs daily without manual steps | ⚪ |
| AI/BI dashboard | Forecast vs. actual, error over time, price drivers | ⚪ |
 
---
 
## Tech stack
 
- **Databricks Free Edition**: Serverless compute, Unity Catalog, Delta Lake, MLflow, Jobs, AI/BI dashboards
- **Databricks Asset Bundles** (`databricks.yml`) to define jobs as code
- **Python 3.12**, **PySpark**, **pandas**, **scikit-learn**, **MLflow**
- **Databricks Connect** and the **Databricks extension for VS Code** for local development
- **uv** for the Python environment
---
 
## Project status
 
| Phase | Status |
| --- | --- |
| 0 — Setup | ✅ Done |
| 1 — Bronze (ingestion) | ✅ Done |
| 2 — Silver (cleaning) | ✅ Done |
| 3 — Gold (features) | ✅ Done |
| 4 — ML with MLflow | ✅ Done |
| 5 — Predictions, Job, dashboard | ⚪ Not started |
| 6 — Polish and publish | ⚪ Not started |
 
---
 
## Repository structure
 
| Folder | Purpose |
| --- | --- |
| `setup/` | Creates the catalog, schemas and Volume (run once) |
| `bronze/` | Downloads SMARD data and builds the Bronze table |
| `silver/` | Cleans and reshapes the data into the Silver table |
| `gold/` | Builds the feature table |
| `ml/` | Trains, evaluates and registers the model with MLflow |
| `explorations/` | SQL checks and API explorations (not part of the pipeline) |
 
---
 
## Next steps / possible version 2
 
- **v1.1 features:** public holiday flag, SMARD forecasts of load / wind / solar
- **v2:** weather forecasts (Open-Meteo), 15-minute forecasts
- Gas and CO₂ prices as extra features
- Deep learning models
- Deployment on Azure
---
 
## Run it yourself
 
Setup instructions will be added once the pipeline is in place.
 