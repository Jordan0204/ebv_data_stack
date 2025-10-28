#!/usr/bin/env python3
import argparse, pathlib, datetime as dt
from scripts.util_io import read_yaml

def check_minute(day: str):
    p = pathlib.Path(f"Data/minute/{day}.yaml")
    if not p.exists():
        raise SystemExit(f"Missing minute file {p}")
    y = read_yaml(str(p))
    rows = y.get("rows", [])
    last_ts = None
    for i, r in enumerate(rows):
        ts = dt.datetime.fromisoformat(r["ts"].replace("Z","+00:00"))
        if last_ts and (ts - last_ts).total_seconds() != 60:
            raise SystemExit(f"Gap or disorder at row {i}: {last_ts} -> {ts}")
        last_ts = ts
    print(f"[minute] rows={len(rows)} ok")

def check_hourly(day: str):
    p = pathlib.Path(f"Reports/hourly/{day}.yaml")
    if not p.exists():
        print(f"[hourly] (no file yet) ok")
        return
    y = read_yaml(str(p))
    bars = y.get("bars", [])
    last = None
    for i, b in enumerate(bars):
        he = dt.datetime.fromisoformat(b["hour_end"].replace("Z","+00:00"))
        if he.minute != 0 or he.second != 0:
            raise SystemExit(f"hour_end not on boundary at idx {i}: {he}")
        if last and he <= last:
            raise SystemExit(f"non-increasing hour_end at idx {i}: {last} -> {he}")
        last = he
    print(f"[hourly] bars={len(bars)} ok")

def check_daily(day: str):
    p = pathlib.Path(f"Reports/daily/{day}.yaml")
    if not p.exists():
        print(f"[daily] (no file yet) ok")
        return
    y = read_yaml(str(p))
    for k in ["o","h","l","c","seal_ts"]:
        if k not in y:
            raise SystemExit(f"daily missing key {k}")
    print(f"[daily] date={y['date']} ok")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-minute", action="store_true")
    ap.add_argument("--check-hourly", action="store_true")
    ap.add_argument("--check-daily", action="store_true")
    ap.add_argument("--day", required=True)
    args = ap.parse_args()
    if args.check_minute: check_minute(args.day)
    if args.check_hourly: check_hourly(args.day)
    if args.check_daily: check_daily(args.day)
