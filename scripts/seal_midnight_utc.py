#!/usr/bin/env python3
import datetime as dt, subprocess, os

def run(cmd):
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)

if __name__ == "__main__":
    now = dt.datetime.now(dt.timezone.utc)
    d_prev = (now.date() - dt.timedelta(days=1)).strftime("%Y-%m-%d")
    run(["python", "scripts/build_daily_from_minute.py", "--day", d_prev])
    run(["python", "scripts/make_daily_table.py", "--limit", "90"])
    if os.environ.get("GIT_AUTOPUSH") == "1":
        run(["git", "add", "Reports/daily", "public/daily_table.csv"])
        run(["git", "commit", "-m", f"seal {d_prev} [daily + table]"])
        run(["git", "push"])
