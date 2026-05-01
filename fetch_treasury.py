"""Fetch annual averages of the FRED 10-year Treasury constant-maturity yield (DGS10).

DGS10 is sourced from the U.S. Treasury and is in the public domain — unlike
Freddie Mac's PMMS (FRED's MORTGAGE30US) which we cannot redistribute. We use
DGS10 + a fixed mortgage-Treasury spread (~1.7%) as a copyright-clean proxy
for the historical 30-year fixed mortgage rate.

Run this whenever you want to refresh the dataset. Stdlib only.

    python fetch_treasury.py
"""
import csv
import io
import json
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DST = ROOT / "treasury_rates.json"
URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"

print(f"Fetching {URL}")
with urllib.request.urlopen(URL, timeout=30) as resp:
    raw = resp.read().decode("utf-8")

reader = csv.DictReader(io.StringIO(raw))
buckets = defaultdict(list)
for row in reader:
    date = row.get("DATE") or row.get("observation_date")
    val = row.get("DGS10")
    if not date or not val or val == ".":
        continue
    try:
        v = float(val)
    except ValueError:
        continue
    year = int(date[:4])
    buckets[year].append(v)

annual = {str(y): round(sum(vs) / len(vs), 3) for y, vs in sorted(buckets.items()) if vs}

DST.write_text(json.dumps(annual, indent=2), encoding="utf-8")
print(f"Wrote {DST}: {len(annual)} years ({min(annual)}-{max(annual)})")
