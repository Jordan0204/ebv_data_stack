#!/usr/bin/env python3
import argparse, pathlib, datetime as dt
from scripts.util_io import read_yaml, write_yaml, sha256_of_json

def build_daily_from_minutes(day: str):
    mpath = pathlib.Path(f"Data/minute/{day}.yaml")
    if not mpath.exists():
        raise SystemExit(f"missing minute file {mpath}")
    y = read_yaml(str(mpath))
    rows = y.get("rows", [])
    if len(rows) < 1:
        raise SystemExit("no minute rows for day")
    o = rows[0]["o"]
    c = rows[-1]["c"]
    h = max(r["h"] for r in rows)
    l = min(r["l"] for r in rows)
    daily = {
        "date": day, "symbol": "BTCUSD", "source": "m1_v1",
        "o": float(o), "h": float(h), "l": float(l), "c": float(c),
        "seal_ts": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    daily["sha256"] = sha256_of_json({k:v for k,v in daily.items() if k!="sha256"})
    dpath = pathlib.Path(f"Reports/daily/{day}.yaml")
    write_yaml(str(dpath), daily)
    return dpath

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", required=True)
    args = ap.parse_args()
    build_daily_from_minutes(args.day)
