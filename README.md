# UnfallAtlas API

UnfallAtlas integrates official German road-accident open data into a normalized PostgreSQL database. It exposes reproducible answers through a documented FastAPI service and a React dashboard, with source and license provenance attached to every data response.

## Architecture

```text
Unfallatlas CSV ─┐
Regionalstatistik├─> async ETL ─> PostgreSQL 15 ─> FastAPI ─> React dashboard
GENESIS CSV/API ─┘       │              │             │
                        └─ import_runs ─┴─ provenance ┘
```

## Prerequisites

- Docker with Compose
- Python 3.11+ for local backend development
- Node.js 18+ for local frontend development

## Quickstart

```bash
cp .env.example .env
# Place the 4 CSV files in ./data/
docker-compose up --build
```

Open the dashboard at `http://localhost:5173`, Swagger UI at `http://localhost:8000/docs`, and health check at `http://localhost:8000/health`.

## ETL

The runner validates expected files, logs each source, continues after failures, and exits non-zero if any source failed.

```bash
cd backend
python -m etl.runner --source all
python -m etl.runner --source unfallatlas
python -m etl.runner --reset
```

Rates without a source year use the documented sentinel `year=0`. Accident imports deduplicate by `UIDENTSTLAE`; regions and indicator values are updated idempotently.

## Tests

```bash
cd backend
pytest -q

cd ../frontend
npm install
npm run build
```

## Data Sources

| Source | Purpose | License |
|---|---|---|
| Unfallatlas | Point-level road accidents | Datenlizenz Deutschland – Namensnennung – Version 2.0 |
| Regionalstatistik | District accident rates | Datenlizenz Deutschland – Namensnennung – Version 2.0 |
| GENESIS Destatis | Monthly accidents and population | Datenlizenz Deutschland – Namensnennung – Version 2.0 |

Every API data response includes `license` and `sources`. `/metadata/sources` additionally exposes retrieval timestamps, checksums, row counts, and run status.

## Mandatory Exam Q&A

| Question | API call |
|---|---|
| Earliest accident year in dataset | `GET /time/earliest` |
| Accidents with personal injury in Saxony 2023 | `GET /accidents/count?state_ags=14&year=2023` |
| From which year is NRW data available | `GET /time/earliest?state_ags=05` |
| From which year is MV data available | `GET /time/earliest?state_ags=13` |
| Pedestrian accidents in Berlin 2023 | `GET /accidents/count?state_ags=11&year=2023&ist_fuss=true` |
| Accidents per 100k inhabitants (cross-source) | `GET /aggregates/rates?year=2023&level=district&top_n=10` |

The count endpoint executes a single `COUNT(*)` query. Aggregates execute SQL `GROUP BY` queries. Rates join accident counts to region population and exclude regions without population.
# dbw_project
This is an academic project which is based on analysing accidents in Germany.
