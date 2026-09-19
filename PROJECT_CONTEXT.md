# PROJECT CONTEXT — ws_MarketAnalytics

## Project Overview

A stock market financial analytics system built on Databricks Free Edition (with Unity Catalog). The system ingests stock market data via the yfinance API, standardizes it through a multi-layer architecture, and produces analytics-ready tables with technical indicators for dashboards and ML models.

| Aspect | Decision |
| --- | --- |
| **Project Name** | `ws_MarketAnalytics` |
| **Platform** | Databricks Free Edition (with Unity Catalog) |
| **Compute** | Serverless only (Python, SQL, sh — no R/Scala) |
| **Version Control** | Databricks Git folder synced to GitHub |
| **CI/CD** | Declarative Automation Bundles (DABs) + GitHub Actions |
| **Environments** | Dev, QA, Prod (separate UC catalogs per environment) |

---

## Environments

Three isolated environments, each with its own Unity Catalog catalog. The DAB bundle defines three targets (`dev`, `qa`, `prod`) that deploy the same code to different catalogs.

| Environment | UC Catalog | DAB Target | Purpose | CI/CD Trigger |
| --- | --- | --- | --- | --- |
| **Dev** | `fin_analytics_dev` | `dev` | Active development, testing | Auto-deploy on merge to `main` |
| **QA** | `fin_analytics_qa` | `qa` | Integration testing, UAT | Manual deploy or tag-based release |
| **Prod** | `fin_analytics_prod` | `prod` | Production analytics | Manual deploy after QA sign-off |

### Environment Promotion Flow

```
Developer commits -> GitHub branch
  -> Pull request: databricks bundle validate --target dev
  -> Merge to main: databricks bundle deploy --target dev
  -> QA sign-off: databricks bundle deploy --target qa
  -> Prod approval: databricks bundle deploy --target prod
```

### Per-Environment Catalog Structure

Each environment has identical schema structure — only the catalog name changes:

| Catalog | Schema | Layer | Key Tables |
| --- | --- | --- | --- |
| `fin_analytics_<env>` | `raw` | Bronze | `stock_prices_raw`, `ticker_reference_raw` |
| `fin_analytics_<env>` | `clean` | Silver | `stock_prices`, `ticker_dim` |
| `fin_analytics_<env>` | `gold` | Gold | `technical_indicators`, `daily_returns`, `sector_performance` |

Where `<env>` is `dev`, `qa`, or `prod`.

### UC Volumes (Per Environment)

| Volume | Purpose |
| --- | --- |
| `/Volumes/fin_analytics_<env>/raw/` | Raw API response files (CSV/JSON) |
| `/Volumes/fin_analytics_<env>/clean/` | Reference configs, seed files |

---

## Architecture: Layer Division

| Layer | Flow | Framework | Language |
| --- | --- | --- | --- |
| **Bronze** | API to Raw tables | Python notebooks (yfinance) | Python |
| **Bronze to Silver** | Raw to Clean/standardized tables | Python framework (PySpark) | Python |
| **Silver to Gold** | Clean to Analytics/indicators | dbt (dbt-databricks adapter) | SQL |
| **Orchestration** | All jobs + deployment | DABs + GitHub Actions | YAML |

---

## Workspace Folder Structure

```
ws_MarketAnalytics/                          (Git folder synced to GitHub)
|
|-- databricks.yml                           # Single DAB bundle root
|-- PROJECT_CONTEXT.md                      # This file - project documentation hub
|
|-- python/                                  # Bronze + Silver layers (PySpark)
|   |-- setup/
|   |   |-- 00_create_catalog_schemas.py      # Create UC catalog, schemas, volumes
|   |-- ingestion/                            # BRONZE: API to Raw tables
|   |   |-- 01_pull_stock_data.py            # yfinance to fin_analytics.raw.stock_prices_raw
|   |   |-- 02_load_reference_data.py        # Load ticker reference to fin_analytics.raw
|   |-- standardization/                      # BRONZE to SILVER: Raw to Clean tables
|   |   |-- 03_standardize_stock_prices.py   # Deduplicate, type-cast, validate OHLCV
|   |   |-- 04_standardize_ticker_dim.py     # Validate, deduplicate reference data
|   |-- utils/
|       |-- __init__.py
|       |-- schema_definitions.py            # PySpark schema definitions
|       |-- data_quality.py                  # Reusable validation functions
|
|-- dbt/                                     # SILVER to GOLD: dbt project (SQL only)
|   |-- dbt_project.yml
|   |-- profiles.yml                          # UC connection (fin_analytics catalog)
|   |-- packages.yml
|   |-- models/
|   |   |-- gold/                             # Only gold layer (sources = clean schema)
|   |       |-- technical_indicators.sql      # SMA, EMA, RSI, MACD, Bollinger
|   |       |-- daily_returns.sql            # Daily returns, volatility
|   |       |-- sector_performance.sql        # Sector-level aggregations
|   |-- schema.yml                            # Sources (fin_analytics.clean) + tests
|   |-- macros/
|   |   |-- rsi.sql
|   |   |-- macd.sql
|   |   |-- bollinger_bands.sql
|   |   |-- moving_average.sql
|   |-- tests/
|       |-- assert_no_negative_volumes.sql
|
|-- resources/                              # DAB resource definitions
|   |-- ingestion_job.yml                    # Bronze ingestion (Python notebooks)
|   |-- standardization_job.yml              # Bronze to Silver (Python notebooks)
|   |-- dbt_job.yml                          # Silver to Gold (dbt run + test)
|
|-- dashboards/                             # Version-controlled dashboards
|   |-- market_overview.lvdash.json
|   |-- stock_detail.lvdash.json
|
|-- tests/                                  # Project-level tests
|   |-- test_ingestion.py
|
|-- .github/
    |-- workflows/
        |-- deploy.yml                       # GitHub Actions CI/CD
```

---

## Layer Details

### Layer 1: Bronze - Python Ingestion

| Notebook | Input | Output Table | Key Logic |
| --- | --- | --- | --- |
| `01_pull_stock_data.py` | yfinance API | `fin_analytics_<env>.raw.stock_prices_raw` | Fetch OHLCV for tickers, append as Delta |
| `02_load_reference_data.py` | CSV/seed file | `fin_analytics_<env>.raw.ticker_reference_raw` | Load ticker symbols, sectors, exchanges |

Responsibilities: API calls, data landing, raw Delta table creation, schema enforcement on write.

### Layer 2: Bronze to Silver - Python Standardization

| Notebook | Input Table | Output Table | Key Logic |
| --- | --- | --- | --- |
| `03_standardize_stock_prices.py` | `fin_analytics_<env>.raw.stock_prices_raw` | `fin_analytics_<env>.clean.stock_prices` | Deduplicate on (ticker, date), type-cast OHLCV, handle nulls, add audit columns |
| `04_standardize_ticker_dim.py` | `fin_analytics_<env>.raw.ticker_reference_raw` | `fin_analytics_<env>.clean.ticker_dim` | Validate, deduplicate, standardize sector/exchange names |

Responsibilities: Data quality checks (nulls, duplicates, type casting), schema standardization, audit columns (ingested_at, processed_at), Delta table optimization (OPTIMIZE, Z-ORDER).

Shared Utils:

| File | Purpose |
| --- | --- |
| `schema_definitions.py` | Centralized PySpark schema objects for all tables |
| `data_quality.py` | Reusable functions: check_nulls(), check_duplicates(), validate_ranges() |

### Layer 3: Silver to Gold - dbt Transformation

| dbt Model | Source (clean) | Target (gold) | Key Logic |
| --- | --- | --- | --- |
| `technical_indicators.sql` | `fin_analytics_<env>.clean.stock_prices` | `fin_analytics_<env>.gold.technical_indicators` | SMA, EMA, RSI, MACD, Bollinger Bands per ticker |
| `daily_returns.sql` | `fin_analytics_<env>.clean.stock_prices` | `fin_analytics_<env>.gold.daily_returns` | Daily returns, rolling volatility, cumulative returns |
| `sector_performance.sql` | `clean.stock_prices` + `clean.ticker_dim` | `fin_analytics_<env>.gold.sector_performance` | Sector-level daily aggregates, sector returns |

dbt sources (schema.yml) reference `fin_analytics_<env>.clean` schema. dbt models write to `fin_analytics_<env>.gold` schema. The `<env>` value is resolved via dbt profiles per target.

---

## Orchestration (DAB Jobs)

```
Job 1: ingestion_job (daily)
  Task 1: 00_create_catalog_schemas  -> ensures catalog/schemas exist (uses DAB variable: catalog)
  Task 2: 01_pull_stock_data          -> yfinance -> fin_analytics_<env>.raw
  Task 3: 02_load_reference_data       -> fin_analytics_<env>.raw
      | (on success)
Job 2: standardization_job
  Task 1: 03_standardize_stock_prices  -> fin_analytics_<env>.raw -> fin_analytics_<env>.clean
  Task 2: 04_standardize_ticker_dim    -> fin_analytics_<env>.raw -> fin_analytics_<env>.clean
      | (on success)
Job 3: dbt_job
  Task 1: pip install dbt-databricks
  Task 2: dbt deps
  Task 3: dbt run --target <env>         -> fin_analytics_<env>.clean -> fin_analytics_<env>.gold
  Task 4: dbt test --target <env>        -> validate gold models
```

Job chain: ingestion_job -> standardization_job -> dbt_job

Each job uses the DAB variable `{{ var.catalog }}` to target the correct environment catalog.

---

## CI/CD (GitHub Actions)

### Deployment Flow

```
                    PR Created
                        |
              +---------+---------+
              |  Validate (dev)     |
              |  dbt parse          |
              +---------+----------+
                        |
                   Merge to main
                        |
              +---------+---------+
              |  Deploy to Dev     |
              |  Run pipeline      |
              +---------+----------+
                        |
                   QA Sign-off
                        |
              +---------+---------+
              |  Deploy to QA      |
              |  Run pipeline      |
              +---------+----------+
                        |
                   Prod Approval
                        |
              +---------+---------+
              |  Deploy to Prod    |
              |  Run pipeline      |
              +---------+----------+
```

### GitHub Actions Triggers

| Trigger | Environment | Action |
| --- | --- | --- |
| **Pull request** | dev | `databricks bundle validate --target dev` + `dbt parse` |
| **Merge to main** | dev | `databricks bundle deploy --target dev` + run pipeline |
| **Tag `qa-*`** | qa | `databricks bundle deploy --target qa` + run pipeline |
| **Tag `prod-*`** | prod | `databricks bundle deploy --target prod` + run pipeline |

### DAB Bundle Targets

```yaml
targets:
  dev:
    default: true
    variables:
      catalog: fin_analytics_dev
  qa:
    variables:
      catalog: fin_analytics_qa
  prod:
    variables:
      catalog: fin_analytics_prod
```

### dbt Profiles (Per Environment)

```yaml
ws_market_analytics:
  outputs:
    dev:
      catalog: fin_analytics_dev
    qa:
      catalog: fin_analytics_qa
    prod:
      catalog: fin_analytics_prod
```

---

## Build Order

| Phase | Step | Deliverable | Depends On |
| --- | --- | --- | --- |
| **1. Foundation** | 1.1 Create Git folder + DAB bundle | `ws_MarketAnalytics/` with `databricks.yml` (3 targets: dev, qa, prod) | -- |
| | 1.2 Create UC catalogs + schemas + volumes | `fin_analytics_dev`, `fin_analytics_qa`, `fin_analytics_prod` (each with `raw`, `clean`, `gold`) | 1.1 |
| | 1.3 Create `PROJECT_CONTEXT.md` | Documentation hub | 1.1 |
| **2. Bronze (Python)** | 2.1 Build `00_create_catalog_schemas.py` | Setup automation (parameterized by env) | 1.2 |
| | 2.2 Build `01_pull_stock_data.py` | yfinance to `fin_analytics_<env>.raw.stock_prices_raw` | 2.1 |
| | 2.3 Build `02_load_reference_data.py` | Ticker reference to `fin_analytics_<env>.raw` | 2.1 |
| | 2.4 Build `utils/` (schemas, data quality) | Shared Python framework | 2.1 |
| | 2.5 Define `ingestion_job.yml` | DAB job definition (uses `{{ var.catalog }}`) | 2.2-2.4 |
| **3. Silver (Python)** | 3.1 Build `03_standardize_stock_prices.py` | `raw` to `clean.stock_prices` | Phase 2 |
| | 3.2 Build `04_standardize_ticker_dim.py` | `raw` to `clean.ticker_dim` | Phase 2 |
| | 3.3 Define `standardization_job.yml` | DAB job definition | 3.1-3.2 |
| **4. Gold (dbt)** | 4.1 Initialize dbt project (`dbt init`) | `dbt/` directory + 3-target profiles | Phase 3 |
| | 4.2 Write gold models + macros | Technical indicators, returns, sector perf | 4.1 |
| | 4.3 Write `schema.yml` tests | Data quality checks on gold models | 4.2 |
| | 4.4 Define `dbt_job.yml` | DAB job definition (uses `--target {{ var.env }}`) | 4.2-4.3 |
| **5. CI/CD** | 5.1 Set up GitHub Actions workflow | `.github/workflows/deploy.yml` (dev, qa, prod triggers) | Phases 2-4 |
| | 5.2 Validate bundle (dev) | `databricks bundle validate --target dev` | 5.1 |
| | 5.3 Deploy to dev | `databricks bundle deploy --target dev` | 5.2 |
| | 5.4 Deploy to qa | `databricks bundle deploy --target qa` (tag `qa-*`) | 5.3 |
| | 5.5 Deploy to prod | `databricks bundle deploy --target prod` (tag `prod-*`) | 5.4 |
| **6. Dashboards** | 6.1 Build Market Overview dashboard | `market_overview.lvdash.json` | Phase 4 |
| | 6.2 Build Stock Detail dashboard | `stock_detail.lvdash.json` | Phase 4 |
| | 6.3 Export dashboards to DAB | Version-controlled (per-env data sources) | 6.1-6.2 |

---

## Key Design Principles

| Principle | How Applied |
| --- | --- |
| **Bronze = Python (ingestion)** | yfinance API calls, raw Delta table creation |
| **Silver = Python (standardization)** | PySpark cleansing, dedup, type-casting, validation |
| **Gold = dbt (transformation)** | SQL-only technical indicators, aggregations, analytics |
| **Single DAB bundle** | One `databricks.yml` governs all 3 jobs + dashboards + 3 targets |
| **UC 3-level namespace** | `fin_analytics_<env>.raw/clean/gold` per environment |
| **Environment isolation** | Separate UC catalogs: `fin_analytics_dev`, `fin_analytics_qa`, `fin_analytics_prod` |
| **Git as source of truth** | All files version-controlled via Git folder |
| **Automated CI/CD** | GitHub Actions: PR -> validate dev, merge -> deploy dev, tag -> deploy qa/prod |
| **Shared Python utils** | Reusable schemas + data quality functions across Bronze and Silver |

---

## Free Edition Constraints

| Constraint | Impact | Mitigation |
| --- | --- | --- |
| Serverless compute only | No R/Scala | Use Python + SQL exclusively |
| Cluster size limits | Smaller compute | Batch ingestion (not streaming); optimize dbt models |
| Token/workspace limits | Lower quotas | Schedule jobs during off-peak; limit data scope |

---

## Data Sources

| Source | Type | Status |
| --- | --- | --- |
| yfinance | Free Python API | Primary - OHLCV stock data |
| Alpha Vantage | Free tier (API key) | Future consideration |
| Polygon.io | Paid | Future consideration |
| SEC EDGAR | Free | Future - fundamental data |

---

## Dashboards (AI/BI)

| Dashboard | Key Widgets | Data Source |
| --- | --- | --- |
| **Market Overview** | Sector heatmap, top 10 movers, index performance | `fin_analytics_<env>.gold.sector_performance` |
| **Stock Detail** | Price chart, technical indicators, volume bars | `fin_analytics_<env>.gold.technical_indicators` |

Dashboards are exported as `.lvdash.json` files and version-controlled within the DAB bundle.

---

## Future Expansion

| Feature | When | Dependency |
| --- | --- | --- |
| ML models (forecasting) | After Phase 6 | Gold layer complete |
| Additional data sources (Alpha Vantage, Polygon) | After Phase 3 | Silver layer stable |
| UC governance tags + policies | After Phase 5 | UC catalog established |
| SDP pipelines (replace Python standardization) | Future | Evaluate if free edition supports SDP |
| Delta Sharing | Future | UC governance in place |

---

*Last updated: 2026-09-20*
*Revision: 2 - Added Dev/QA/Prod multi-environment support*
*Project owner: swapnilshekhar1493@gmail.com*