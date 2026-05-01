# Buy vs Rent + Invest — Retrospective Lab

A static dashboard that compares two parallel financial paths over the past *X* years using identical cash flows:

- **Path A — Buy:** down payment → house, monthly PITI + HOA, sell at year *X*.
- **Path B — Rent + Invest:** down payment → stock lump sum, pay rent monthly, reinvest the rent-vs-mortgage surplus year by year.

Both paths receive the same annual cash budget (`monthly × 12 + down_payment_year_0`). Final wealth is what determines the winner.

There are **two pages**:

| File | What it's for |
| --- | --- |
| `buy_vs_rent.html` | Step-by-step walkthrough (6 panels, learn the model) |
| `buy_vs_rent_quick.html` | All inputs in one form, single button, details collapsed |

The quick file is **generated** from the step-by-step file by `_build_quick.py` — edit the master and rebuild, don't edit the quick file by hand.

## Run locally

The pages need to be served over HTTP (browsers block `fetch()` of local files via `file://`). Easiest:

```bash
python -m http.server 8765
```

Then open <http://localhost:8765/buy_vs_rent_quick.html>.

## Inputs

**Basics**
- Years to analyze (X), Loan term, Monthly housing budget (PITI + HOA all-in), Down payment, Stock ticker.

**Buy & Carry (CA)**
- HOA, mortgage rate, insurance rate, marginal tax rate, SALT cap.
- Home price is **not** a direct input — it's solved from the affordability formula (Chase-style):
  `H = (M − HOA + D·a) / (a + (t + i)/12)` where `a` is the monthly amortization factor.

**Sale**
- ZIP, sale year, closing cost %, optional purchase / sale price overrides.
- Default sale = `purchase_price × HPI_ratio` from FHFA ZIP5 annual data.

**Rent**
- Annual rent escalation %, optional starting rent override.

## Stock prices — two modes

- **Cached (default for the 5 popular tickers):** check the `use cached` box to pick from `VOO / AAPL / GOOG / QCOM / NVDA`. Reads `./stocks/<TICKER>.json` directly — no API call, no key. Covers the last 20 years.
- **Live (any other ticker):** uncheck `use cached`. Fetches monthly adjusted close from [Alpha Vantage](https://www.alphavantage.co). Free tier is 25 calls/day — paste your free key into the API-key field. Results are cached in `localStorage` for 24h to stay well under the quota.

If your purchase year falls before `currentYear − 20`, the cached toggle is auto-disabled.

## Updating data

### Refresh stock cache (`./stocks/`)

Adds or refreshes a ticker's JSON file from Yahoo (via `yfinance`):

```bash
python -m venv .venv
.venv\Scripts\pip install yfinance              # Windows
# .venv/bin/pip install yfinance                 # macOS/Linux

.venv\Scripts\python fetch_stock.py VOO AAPL GOOG QCOM NVDA
```

If you cache a new ticker, also add it to the `<select id="tickerSelect">` block in `buy_vs_rent.html` and the matching block in `_build_quick.py`, and append it to `CACHED_TICKERS` in the JS — then rebuild the quick file (below).

### Refresh FHFA HPI (`hpi_at_zip5.json`)

FHFA publishes annual ZIP5 HPI updates a few times a year. To pick up a new vintage:

```bash
# 1. Download fresh xlsx from FHFA (~40 MB, gitignored locally)
curl -L -o hpi_at_zip5.xlsx \
  https://www.fhfa.gov/hpi/download/annual/hpi_at_zip5.xlsx

# 2. Convert to compact JSON (~10 MB)
.venv\Scripts\pip install openpyxl
.venv\Scripts\python convert_hpi.py
```

The xlsx is in `.gitignore` — only the JSON ships in the repo.

### Rebuild the quick file

After any change to `buy_vs_rent.html` (markup, JS, CSS), regenerate the single-form variant:

```bash
.venv\Scripts\python _build_quick.py
```

The script reads `buy_vs_rent.html`, splices its inputs into one panel, wraps each step's output in a `<details>` collapsible, and writes `buy_vs_rent_quick.html`. Don't edit `buy_vs_rent_quick.html` directly — your edits will be overwritten on the next rebuild.

## Deploying

Everything is static. ~10 MB total — drop the repo onto any static host:

- **Cloudflare Pages / Netlify / Vercel:** connect the repo, no build command, publish directory `/`. Done.
- **DigitalOcean App Platform → Static Site:** same, free for the first 3 sites.
- **Any S3 / Spaces / nginx:** copy the folder to the bucket / `/var/www/html`.

No build step or backend is needed at deploy time. The only dynamic moving part is the optional Alpha Vantage call — which happens client-side, with the user's own key.

## Sources & references

The model is documented inline in the page footer, but for convenience:

- Sale price & appreciation — [FHFA House Price Index Calculator](https://www.fhfa.gov/data/hpi/datasets?tab=hpi-calculator)
- Tax-deduction model — [Freddie Mac Tax Savings Calculator](https://myhome.freddiemac.com/resources/calculators/tax-savings)
- Mortgage rate history — [FRED 30-Yr Fixed Mortgage Average](https://fred.stlouisfed.org/series/MORTGAGE30US)
- Amortization / loan-balance math — [Bankrate Amortization Calculator](https://www.bankrate.com/mortgages/amortization-calculator/)
- Home-price affordability formula — [Chase Affordability Calculator](https://www.chase.com/personal/mortgage/calculators-resources/affordability-calculator)

## Caveats

- All comparisons are **nominal** — no inflation/discount-rate adjustment. Wealth at year *X* in dollars-of-year-*X*.
- Tax-deduction model assumes itemizing and applies the SALT cap to property tax only (state income tax is presumed to consume the rest of the cap separately).
- HPI is at the **ZIP5 annual developmental** granularity — noisier than the FHFA web tool's quarterly MSA series. The "Sale Price (override)" input is for when you want to pin the sale to FHFA web's number directly.
- No capital-gains tax modeling on either path. For a primary-residence sale, the federal $250K / $500K exclusion typically zeros it; for the stock side, you're on your own.

## Layout

```
.
├── README.md
├── .gitignore
├── buy_vs_rent.html          # step-by-step walkthrough (master)
├── buy_vs_rent_quick.html    # generated · do not edit
├── hpi_at_zip5.json          # FHFA ZIP5 annual HPI (~10 MB)
├── stocks/                   # cached year-end adjusted closes
│   ├── VOO.json
│   ├── AAPL.json
│   ├── GOOG.json
│   ├── QCOM.json
│   └── NVDA.json
├── fetch_stock.py            # tool · refresh ./stocks/<TICKER>.json
├── convert_hpi.py            # tool · xlsx → hpi_at_zip5.json
└── _build_quick.py           # tool · regenerate buy_vs_rent_quick.html
```
