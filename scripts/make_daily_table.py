#!/usr/bin/env python3
import pathlib, csv
from scripts.derive_atr14_v1 import load_daily_rows, wilder_atr14

BUF_PCT = 0.15

def main(limit: int=90):
    dailies = load_daily_rows(limit=limit)
    atr14 = dict(wilder_atr14(dailies))
    outp = pathlib.Path("public/daily_table.csv")
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Date","Symbol","High","Low","Close","ATR14","BufPct","Buffer","GreenRail","RedRail"])
        for d in dailies:
            date = d["date"]
            h,l,c = d["h"], d["l"], d["c"]
            atr = atr14.get(date)
            buf = (atr * BUF_PCT) if atr is not None else ""
            green = (h + buf) if buf != "" else ""
            red = (l - buf) if buf != "" else ""
            w.writerow([date, "BTCUSD", f"{h:.2f}", f"{l:.2f}", f"{c:.2f}",
                        f"{atr:.2f}" if atr is not None else "", f"{BUF_PCT:.2f}", 
                        f"{buf:.3f}" if buf != "" else "", 
                        f"{green:.2f}" if green != "" else "", 
                        f"{red:.2f}" if red != "" else ""])

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=90)
    args = ap.parse_args()
    main(limit=args.limit)
