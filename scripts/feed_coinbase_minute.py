#!/usr/bin/env python3
"""
Live minute feed loop (Coinbase Exchange REST) — robust boundary timing
"""
import json, time, urllib.request, urllib.parse, os, sys
import datetime as dt, pathlib, subprocess
from scripts.util_io import read_yaml, write_yaml
from scripts.util_time import next_minute_boundary, floor_minute

PRODUCT_ID = "BTC-USD"

def _iso(ts: dt.datetime) -> str:
    return ts.replace(tzinfo=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _get(url: str):
    req = urllib.request.Request(url, headers={
        "Accept":"application/json",
        "User-Agent":"ebv-feed/1.0 (+local)"
    })
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))

def fetch_last_closed_minute(product_id: str, last_open: dt.datetime):
    """Return dict for [last_open, last_open+60s).
    Coinbase may label the bucket at either the start (target) or end (target+60).
    """
    start_iso = _iso(last_open)
    end_iso   = _iso(last_open + dt.timedelta(minutes=1))
    base = "https://api.exchange.coinbase.com"
    q = urllib.parse.urlencode({"granularity": 60, "start": start_iso, "end": end_iso})
    url = f"{base}/products/{product_id}/candles?{q}"
    data = _get(url)  # [[time, low, high, open, close, volume], ...]
    # Fallback: recent batch if window is empty or delayed
    if not data:
        data = _get(f"{base}/products/{product_id}/candles?granularity=60")
    target = int(last_open.replace(tzinfo=dt.timezone.utc).timestamp())
    for b in data:
        t = int(b[0])
        if t == target or t == target + 60:  # tolerate end-labeled bucket
            return {"ts": start_iso, "o": float(b[3]), "h": float(b[2]),
                    "l": float(b[1]), "c": float(b[4]), "v": float(b[5])}
    raise RuntimeError(f"no candle returned for {start_iso} (tried target={target} and target+60)")

def append_minute_row(day_path: pathlib.Path, day: str, row: dict):
    if day_path.exists():
        y = read_yaml(str(day_path))
    else:
        y = {"date": day, "symbol": "BTCUSD", "granularity": "m1", "rows": []}
    if not any(r["ts"] == row["ts"] for r in y["rows"]):
        y["rows"].append(row)
        y["rows"].sort(key=lambda r: r["ts"])
        write_yaml(str(day_path), y)
        print(f"[feed] appended {row['ts']} -> {day_path}", flush=True)
    else:
        print(f"[feed] already have {row['ts']} -> {day_path}", flush=True)

def main_loop():
    print(f"[feed] started pid={os.getpid()} @ {_iso(dt.datetime.now(dt.timezone.utc))}", flush=True)
    while True:
        # 1) sleep to the next minute boundary
        wake = next_minute_boundary()
        now = dt.datetime.now(dt.timezone.utc)
        to_sleep = (wake - now).total_seconds()
        if to_sleep > 0:
            time.sleep(to_sleep)
        # tiny buffer for exchange publish latency
        time.sleep(2)
        # 2) now we are at wake; the just-closed minute is [wake-60s, wake)
        last_open = (wake - dt.timedelta(minutes=1)).replace(second=0, microsecond=0, tzinfo=dt.timezone.utc)
        try:
            row = fetch_last_closed_minute(PRODUCT_ID, last_open)
            day = last_open.date().strftime("%Y-%m-%d")
            dpath = pathlib.Path(f"Data/minute/{day}.yaml")
            append_minute_row(dpath, day, row)
            if wake.minute == 0:
                print(f"[feed] sealing hour {wake.strftime('%Y-%m-%dT%H:%MZ')} for {day}", flush=True)
                subprocess.call([
                    sys.executable, "scripts/build_hourlies_from_minute.py",
                    "--day", day, "--hour-end", wake.strftime("%Y-%m-%dT%H:%M:%SZ")
                ])
        except Exception as e:
            print("[feed] warn:", e, flush=True)

if __name__ == "__main__":
    # Immediate append targets the PREVIOUS minute: floor(now) - 60s
    try:
        now = dt.datetime.now(dt.timezone.utc)
        last_open = (floor_minute(now) - dt.timedelta(minutes=1)).replace(tzinfo=dt.timezone.utc)
        row = fetch_last_closed_minute(PRODUCT_ID, last_open)
        day = last_open.date().strftime("%Y-%m-%d")
        dpath = pathlib.Path(f"Data/minute/{day}.yaml")
        append_minute_row(dpath, day, row)
    except Exception as e:
        print("[feed] immediate warn:", e, flush=True)
    main_loop()
