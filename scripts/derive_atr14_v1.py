#!/usr/bin/env python3
import pathlib
from typing import List, Tuple, Optional
from scripts.util_io import read_yaml

def load_daily_rows(limit: int=200) -> List[dict]:
    ddir = pathlib.Path("Reports/daily")
    items = []
    for p in sorted(ddir.glob("*.yaml")):
        y = read_yaml(str(p))
        items.append(y)
    return items[-limit:]

def true_range(prev_close: float, h: float, l: float, o: float) -> float:
    a = h - l
    b = abs(h - prev_close)
    c = abs(l - prev_close)
    return max(a, b, c)

def wilder_atr14(dailies: List[dict]) -> List[Tuple[str, Optional[float]]]:
    out = []
    prev_c = None
    trs = []
    for i, d in enumerate(dailies):
        o,h,l,c = d["o"], d["h"], d["l"], d["c"]
        tr = (h - l) if prev_c is None else true_range(prev_c, h, l, o)
        trs.append(tr)
        if i == 13:
            atr = sum(trs[:14]) / 14.0
        elif i > 13:
            atr_prev = out[-1][1]
            atr = (atr_prev * 13 + tr) / 14.0 if atr_prev is not None else None
        else:
            atr = None
        out.append((d["date"], atr))
        prev_c = c
    return out
