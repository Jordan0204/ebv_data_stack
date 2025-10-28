#!/usr/bin/env python3
# Write a synthetic minute day for testing
import argparse, pathlib, random, datetime as dt
from scripts.util_io import write_yaml

def gen_day(day: str, base: float=114000.0):
    daydt = dt.date.fromisoformat(day)
    start = dt.datetime.combine(daydt, dt.time(0,0,tzinfo=dt.timezone.utc))
    rows = []
    cur = base
    rnd = random.Random(hash(day) & 0xffffffff)
    for i in range(60*24):
        t = start + dt.timedelta(minutes=i)
        move = (rnd.random() - 0.5) * 2.0  # -1..+1
        cur = max(1.0, cur + move)
        m_open = cur - move/2
        m_close = cur + move/2
        high = max(m_open, m_close) + rnd.random()*0.2
        low = min(m_open, m_close) - rnd.random()*0.2
        vol = 1.0 + rnd.random()*0.5
        rows.append({
            "ts": t.strftime("%Y-%m-%dT%H:%M:00Z"),
            "o": round(float(m_open), 2),
            "h": round(float(high), 2),
            "l": round(float(low), 2),
            "c": round(float(m_close), 2),
            "v": round(float(vol), 6),
        })
    y = {"date": day, "symbol": "BTCUSD", "granularity": "m1", "rows": rows}
    p = pathlib.Path(f"Data/minute/{day}.yaml")
    write_yaml(str(p), y)
    print(f"[demo] wrote {p} with {len(rows)} rows")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", required=True)
    args = ap.parse_args()
    gen_day(args.day)
