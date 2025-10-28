SHELL := /bin/bash
PY := python

DAY ?= $(shell date -u +%F)

.PHONY: demo clean_demo verify seal

demo:
	@PYTHONPATH=. $(PY) tests/synth_minutes.py --day $(DAY)
	@PYTHONPATH=. $(PY) scripts/build_hourlies_from_minute.py --day $(DAY)
	@PYTHONPATH=. $(PY) scripts/build_daily_from_minute.py --day $(DAY)
	@PYTHONPATH=. $(PY) scripts/make_daily_table.py --limit 60

clean_demo:
	rm -f Data/minute/*.yaml Reports/hourly/*.yaml Reports/daily/*.yaml public/daily_table.csv

verify:
	@PYTHONPATH=. $(PY) scripts/guards.py --check-minute --day $(DAY) && echo "[OK] minute guards"
	@PYTHONPATH=. $(PY) scripts/guards.py --check-hourly --day $(DAY) && echo "[OK] hourly guards (partial ok if intraday)"
	@PYTHONPATH=. $(PY) scripts/guards.py --check-daily --day $(DAY) && echo "[OK] daily guards (if exists)"

seal:
	@PYTHONPATH=. $(PY) scripts/seal_midnight_utc.py
