# Bitcoin KPI Pipeline

An automated data pipeline that fetches live Bitcoin prices from a REST API, computes KPIs, tracks CI/CD pipeline efficiency, and visualises everything in a 4-panel engineering dashboard — all running on GitHub Actions.

---

## What It Does

Every pipeline run:
1. Fetches the current Bitcoin price and 24h change from the CoinGecko REST API
2. Computes KPIs (avg, min, max price, latest 24h change)
3. Logs whether the run succeeded or failed
4. Generates a 4-panel dashboard as `output/chart.png`
5. Commits the updated data and chart back to the repo

---

## Project Structure

```
├── scripts/
│   ├── fetch.py          # REST API → data/data.csv
│   ├── process_data.py   # CSV → KPIs (avg, min, max, 24h change)
│   ├── visualize.py      # KPIs + build log → 4-panel dashboard
│   └── log_build.py      # Logs success/failure to data/build_log.csv
├── tests/
│   ├── test_kpis.py      # Unit tests for KPI computation
│   └── test_build_kpi.py # Unit tests for pipeline efficiency KPI
├── data/
│   ├── data.csv          # Accumulated price history
│   └── build_log.csv     # Pipeline run history (success/failure)
├── output/
│   └── chart.png         # Generated dashboard
├── main.py               # Pipeline orchestrator
├── requirements.txt
└── .github/workflows/
    └── pipeline.yml      # GitHub Actions CI/CD
```

---

## Dashboard — output/chart.png

Four panels generated on every run:

| Panel | Content |
|-------|---------|
| Top left | Bitcoin price over time (styled line chart) |
| Top right | 24h change per data point (green/red bars) |
| Bottom left | KPI stat cards — avg, min, max, latest change |
| Bottom right | Pipeline efficiency donut — success % vs failure % |

---

## CI/CD Pipeline

Three jobs run in sequence on every push and every 30 minutes via cron:

```
push / schedule
      │
      ▼
[1. build]  Install deps → run unit tests
      │ pass
      ▼
[2. test]   Install deps → run unit tests → run main.py
      │ pass
      ▼
[3. run]    Run main.py → commit data + chart → push
```

**Key design decisions:**

- `concurrency: group: pipeline` — prevents simultaneous runs from conflicting over the same files
- `git pull --rebase --autostash -X theirs` — always keeps the freshest generated data on conflict
- `[skip ci]` on auto-commits — prevents infinite pipeline loops

---

## KPIs Tracked

**Price KPIs** (from CoinGecko API):
- Average, minimum, maximum Bitcoin price in EUR
- Latest 24-hour percentage change

**Pipeline Efficiency KPI** (from build_log.csv):
- Total runs recorded
- Success count and failure count
- Success rate as a percentage

---

## Running Locally

```bash
# Clone the repo
git clone https://github.com/MomenWael429/data-pipeline-kpi.git
cd data-pipeline-kpi

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run unit tests
python -m pytest

# Run the full pipeline
python main.py
```

The dashboard will be saved to `output/chart.png`.

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.10 | Core language |
| requests | REST API calls |
| pandas | Data processing |
| matplotlib | Dashboard visualisation |
| pytest | Unit testing |
| GitHub Actions | CI/CD automation |
| CoinGecko API | Live Bitcoin price data |

---

## What I Learned

Committing generated files back to git is not standard practice — it causes merge conflicts when pipeline runs overlap. The production approach would be to store data in a database (PostgreSQL, InfluxDB) and serve the dashboard from cloud storage (S3, Azure Blob). For this project, `concurrency` groups and `-X theirs` rebase strategy were used as a pragmatic solution.

---

## Author

Momen Wael — [github.com/MomenWael429](https://github.com/MomenWael429)
