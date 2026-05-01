---
name: extend-buy-vs-rent
description: Add or modify pieces of the Buy vs Rent + Invest dashboard. Use when the user wants to add a cached stock ticker, add a new input field, change a formula (affordability / amortization / tax / rent / sale / stock), add a new analysis step, or refresh the FHFA HPI / stock data. Triggers on requests to extend, modify, or refresh anything in this repo.
---

# Extending the Buy vs Rent dashboard

## Architecture in 30 seconds

- `buy_vs_rent.html` is the **master** — always edit this.
- `index.html` is **generated** by `_build_quick.py`. Never edit it directly; rebuild instead. The build reads the master, splices its inputs into one consolidated panel, and wraps each step's output block in a `<details>` collapsible.
- All compute functions chain through `computeCompare()`, which `computeAll()` (in the quick file) wraps. Each `computeX()` reads inputs from the DOM, validates, populates a global state object, renders into stable element IDs, and returns the state.

State globals (in the `<script>` block, near the top):

| Global | Set by | Holds |
| --- | --- | --- |
| `housingState` | `computeHousing()` | home price, loan amount, balance@X, totals |
| `rentState`    | `computeRent()`    | starting/end rent, total, year-by-year rows |
| `saleState`    | `computeSale()`    | HPI ratio, sale price, net proceeds, profit |
| `stockState`   | `computeStocks()`  | ticker, start/end price, shares, end value |
| `stockCache`   | `loadStock()`      | in-memory ticker → data |
| `hpiData`      | `loadHPI()`        | full ZIP5 HPI map |
| `treasuryRates`| `loadTreasuryRates()` | year → 10-yr Treasury annual avg (DGS10) |

Element IDs are **flat / unscoped** — the master file has them inside step panels; the quick file moves outputs into `<details>` blocks but keeps IDs identical. **All IDs must be globally unique.** Prefixes by step: `r*` (rent), `k*` (stock), `s*` (sale), `cmp*` (compare), `h*` / `d*` / `l*` (housing).

## Always rebuild after editing the master

```bash
.venv\Scripts\python _build_quick.py
```

If there is no `.venv`, set it up once:

```bash
python -m venv .venv
.venv\Scripts\pip install yfinance openpyxl
```

## Recipe — add a cached stock ticker

1. Fetch its full history:
   ```bash
   .venv\Scripts\python fetch_stock.py NEWTICKER
   ```
   This writes `stocks/NEWTICKER.json`.
2. In `buy_vs_rent.html`: add an `<option value="NEWTICKER">NEWTICKER — Full Name</option>` inside `<select id="tickerSelect">`.
3. In `_build_quick.py`: mirror the same `<option>` line (search for `tickerSelect` in the script).
4. In `buy_vs_rent.html`: add the symbol to the `CACHED_TICKERS = [...]` array.
5. Update the visible hint text in two places (master and build script) — search for `cachedHint` and the `VOO / AAPL / GOOG / QCOM / NVDA` string.
6. Rebuild the quick file.

## Recipe — add a new input field

1. Add the `<input id="newField" ...>` to the relevant Step panel in `buy_vs_rent.html` (inside that step's `<div class="form-grid">`).
2. In `_build_quick.py`, mirror the field into the consolidated inputs panel under the matching subgroup (`Basics` / `Buy & Carry (CA)` / `Sale` / `Rent`).
3. Read it inside the right `computeX()`:
   ```js
   const x = parseFloat(document.getElementById('newField').value);
   if (isNaN(x) || x < 0) return showErrorN('newField must be ≥ 0.');
   ```
4. Add the ID to the keyboard handler's branch list:
   ```js
   if (['existingIds', ..., 'newField'].includes(id)) computeX();
   ```
5. If the value should persist across reloads, follow the `STORAGE_KEY` / `restore()` / `saveParams()` pattern.
6. Rebuild.

## Recipe — change a formula

Find it in one of the `compute*` functions:

| Formula | Function | Search anchor |
| --- | --- | --- |
| Affordability (back-solve home price) | `computeHousing` | `H = (monthlyForHousing + p.downpay * a)` |
| Monthly amortization factor `a` | `computeHousing` | `monthlyRate * Math.pow(1 + monthlyRate, totalMonths)` |
| Year-by-year interest split | `computeHousing` | `for (let y = 0; y < p.years; y++)` |
| Tax savings (interest + capped property tax) | `computeHousing` | `yearDeductible = yearInterest + Math.min(annualPropTax, saltCap)` |
| Sale price (HPI ratio × base) | `computeSale` | `salePrice = saleOverridden ? actualSale : purchaseBase * ratio` |
| Net sale proceeds | `computeSale` | `netSaleProceeds = salePrice - closingCost - h.balance` |
| Path A profit | `computeSale` / `computeCompare` | `profit = netSaleProceeds - totalSpent + taxSavings` |
| Rent escalation | `computeRent` | `monthlyRent *= (1 + r)` |
| Path B annual surplus reinvestment | `computeCompare` | `const surplus = annualMonthlyA - annualRent;` |

When you change a formula, also update its **rendered detail string** (the `dim` text alongside the number) so users see what's actually being computed. Search for `set('xDetail', ...)` near the formula.

## Recipe — add a new compute step

1. In `buy_vs_rent.html`: add a `<div class="panel">` with input + output sections, plus an entry in `<div class="step-bar">`.
2. Add a `computeStepN()` function and matching `showErrorN`/`clearErrorN`.
3. If downstream steps need its output, store a global `stepNState`.
4. To make `computeCompare()` chain it:
   ```js
   if (!await computeStepN()) return showError6('Step N failed — fix it above.');
   ```
5. In `_build_quick.py`:
   - Add the new inputs to the right subgroup of the all-inputs panel.
   - Add a `<details class="detail-block">` block containing the step's output (mirror the existing ones — search for `detail-block` in the build script).
6. Rebuild.

## Recipe — refresh the FHFA HPI dataset

```bash
curl -L -o hpi_at_zip5.xlsx https://www.fhfa.gov/hpi/download/annual/hpi_at_zip5.xlsx
.venv\Scripts\python convert_hpi.py
```

The xlsx is gitignored; only `hpi_at_zip5.json` (~10 MB) ships in the repo.

## Recipe — refresh `treasury_rates.json`

Stdlib only, no key:

```bash
python fetch_treasury.py
```

Pulls FRED's `DGS10` (10-yr Treasury, public-domain US Treasury data), computes annual averages. Used by the auto-mortgage-rate feature: rate = `DGS10[purchaseYear] + MORTGAGE_TREASURY_SPREAD` (currently 1.7%). Do **not** ship Freddie Mac PMMS / FRED `MORTGAGE30US` — that series is proprietary and can't be redistributed; the spread approach is the workaround.

## Recipe — refresh cached stock data

```bash
.venv\Scripts\python fetch_stock.py VOO AAPL GOOG QCOM NVDA
```

Re-run when prices need refreshing (the data is annual; once a year is plenty).

## Test checklist after any change

1. Run a local server: `python -m http.server 8765`.
2. Open `http://localhost:8765/buy_vs_rent.html` — fill inputs, run each step, watch for console errors.
3. Open `http://localhost:8765/` (serves `index.html`) — fill the same inputs, click `Calculate All Paths`, expand every `<details>` block.
4. Compare: both pages should produce **identical** Path A vs Path B numbers and verdict.
5. Mismatch ⇒ the build script's HTML diverged from the master's. Re-check that the inputs you added are mirrored into `_build_quick.py`.

## Conventions to follow

- **Edit the master, never the generated file.** If the quick file looks wrong, rebuild — don't patch it.
- **No backend.** Everything must work as static files served over HTTP.
- **Keep IDs unique** across the whole document — the quick file flattens them all.
- **Update the rendered detail strings** when you change a formula so the UI explains the new math.
- **Add references to the Sources block** at the bottom if a new formula has a public source worth citing.
- **Update this skill** when adding non-obvious extension patterns.
