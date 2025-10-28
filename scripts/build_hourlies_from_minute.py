#!/usr/bin/env python3
import argparse, pathlib, datetime as dt
from scripts.util_io import read_yaml, write_yaml
from scripts.util_time import hour_bounds_ending_at

def select_minutes(rows, start, end):
    out = []
    for r in rows:
        ts = dt.datetime.fromisoformat(r["ts"].replace("Z","+00:00"))
        if start <= ts < end: out.append((ts, r))
    return out

def append_hour_bar(day: str, hour_end: dt.datetime):
    mpath = pathlib.Path(f"Data/minute/{day}.yaml")
    if not mpath.exists(): raise SystemExit(f"missing minute file {mpath}")
    my = read_yaml(str(mpath)); rows = my.get("rows", [])
    start, end = hour_bounds_ending_at(hour_end)
    sel = select_minutes(rows, start, end)
    if not sel: return False
    o = sel[0][1]["o"]; c = sel[-1][1]["c"]
    h = max(r["h"] for _, r in sel); l = min(r["l"] for _, r in sel)

    hpath = pathlib.Path(f"Reports/hourly/{day}.yaml")
    hy = read_yaml(str(hpath)) if hpath.exists() else {"date": day, "symbol": "BTCUSD", "source": "m1_v1", "bars": []}
    hour_end_s = hour_end.replace(tzinfo=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if any(b["hour_end"] == hour_end_s for b in hy["bars"]): return False
    hy["bars"].append({"hour_end": hour_end_s, "o": float(o), "h": float(h), "l": float(l), "c": float(c),
                       "seal_ts": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
    hy["bars"].sort(key=lambda b: b["hour_end"])
    write_yaml(str(hpath), hy)
    return True

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", required=True)
    ap.add_argument("--hour-end")
    a = ap.parse_args()
    if a.hour_end: he = dt.datetime.fromisoformat(a.hour_end.replace("Z","+00:00"))
    else:
        now = dt.datetime.now(dt.timezone.utc)
        he = now.replace(minute=0, second=0, microsecond=0)
    append_hour_bar(a.day, he)
