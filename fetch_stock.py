"""Cache historical stock prices for the buy-vs-rent dashboard.

Usage:
    python fetch_stock.py SPY VTI QQQ
    python fetch_stock.py            # defaults to SPY

Writes ./stocks/<TICKER>.json with year-end (annual) and month-end (monthly)
adjusted close prices in the shape:
    { "ticker": "SPY",
      "annual":  { "2010": 125.75, "2011": 125.50, ... },
      "monthly": { "2010-01": ..., "2010-02": ..., ... } }
"""
import json
import os
import sys

import yfinance as yf

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stocks")
os.makedirs(OUT_DIR, exist_ok=True)

tickers = [t.upper() for t in sys.argv[1:]] or ["SPY"]

for ticker in tickers:
    print(f"Fetching {ticker} ...", end=" ", flush=True)
    try:
        hist = yf.Ticker(ticker).history(period="max", interval="1mo", auto_adjust=True)
    except Exception as e:
        print(f"ERROR: {e}")
        continue
    if hist.empty:
        print("no data")
        continue

    monthly = {}
    annual = {}
    for ts, row in hist.iterrows():
        close = float(row["Close"])
        if close <= 0 or close != close:
            continue
        monthly[ts.strftime("%Y-%m")] = round(close, 4)
        annual[str(ts.year)] = round(close, 4)

    path = os.path.join(OUT_DIR, f"{ticker}.json")
    with open(path, "w") as f:
        json.dump({"ticker": ticker, "annual": annual, "monthly": monthly},
                  f, separators=(",", ":"))
    yrs = sorted(int(y) for y in annual)
    print(f"OK {yrs[0]}-{yrs[-1]} ({len(annual)} years) -> {path}")
