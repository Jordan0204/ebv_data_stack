# EBV Data Stack — Minute → Hourly → Daily (v1.0)

Deterministic, UTC-only data pipeline for BTC-USD:
- **Feed** (minute) → `Data/minute/YYYY-MM-DD.yaml`
- **Hourly builder** → `Reports/hourly/YYYY-MM-DD.yaml` (append 1 sealed bar each hour)
- **Daily builder** → `Reports/daily/YYYY-MM-DD.yaml` (sealed at UTC rollover)
- **ATR14 + Rails** → `public/daily_table.csv` (for Google Sheets IMPORTDATA)
- **Guards** enforce counts, ordering, and immutability of sealed artifacts.

This repo ships with a **demo mode** that synthesizes a fake day of minute data, runs the builders, and produces your `daily_table.csv` so you can **prove the pipeline** before going live.

> Live Coinbase adapter stub is included; you can wire it later with your API choice while keeping the contract unchanged.

## Quick Demo (no internet, no API keys)

```bash
# 0) Create venv (optional)
python3 -m venv .venv && source .venv/bin/activate

# 1) Install deps
pip install -r requirements.txt

# 2) Run demo: writes a synthetic day (D), builds hourlies & daily, then the daily table
make demo

# 3) Inspect artifacts
ls -R Data Reports public

# 4) Verify guards
make verify

# 5) (Optional) Re-run demo to overwrite D with a new synthetic day and re-derive
make clean_demo demo
```

## Going Live (outline)

- Turn on the **feed**: a minute loop that fetches the just-closed minute candle and appends it to `Data/minute/D.yaml`.
- The feed triggers the **hourly builder** right after the top of each hour to append one sealed hourly O/H/L/C bar to `Reports/hourly/D.yaml`.
- A midnight LaunchAgent calls `seal_midnight_utc.py` to build the **daily O/H/L/C** for `D-1`, update `public/daily_table.csv`, and (optionally) commit/push.
