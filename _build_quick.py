"""Transform buy_vs_rent.html into a single-form quick-compare layout.

Reads the original file, keeps the <head> CSS and <script> JS verbatim,
and replaces the body with: (1) one all-inputs panel + Calculate button,
(2) a top-level always-visible summary, (3) collapsible <details> blocks
for each step's outputs.
"""
import re
from pathlib import Path

ROOT = Path(r"C:\Users\user1\Documents\house")
SRC = ROOT / "buy_vs_rent.html"
DST = ROOT / "buy_vs_rent_quick.html"

src = SRC.read_text(encoding="utf-8")

# 1. Title swap
src = src.replace(
    "<title>Buy vs Rent · Retrospective Lab</title>",
    "<title>Buy vs Rent · Quick Compare</title>",
)

# 2. Inject extra CSS just before </style>
extra_css = r"""
  /* --- Quick-compare layout additions --- */
  .subgroup-label {
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--amber);
    margin: 28px 0 12px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
  }
  .subgroup-label:first-child { margin-top: 0; }

  details.detail-block {
    border: 1px solid var(--border);
    border-radius: 2px;
    background: var(--panel);
    margin-top: 12px;
    position: relative;
    overflow: hidden;
  }
  details.detail-block > summary {
    list-style: none;
    cursor: pointer;
    padding: 14px 24px;
    font-size: 11px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--amber-dim);
    display: flex;
    align-items: center;
    gap: 12px;
    user-select: none;
    transition: color 0.15s, background 0.15s;
  }
  details.detail-block > summary::-webkit-details-marker { display: none; }
  details.detail-block > summary::before {
    content: '+';
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    border: 1px solid var(--amber-dim);
    border-radius: 2px;
    font-size: 13px;
    color: var(--amber-dim);
    flex-shrink: 0;
  }
  details.detail-block[open] > summary::before { content: '−'; }
  details.detail-block > summary:hover { color: var(--amber); background: rgba(240,165,0,0.03); }
  details.detail-block .detail-content {
    padding: 24px;
    border-top: 1px solid var(--border);
  }
  details.detail-block .summary {
    /* prevent collision with our own .summary class inside details */
    display: block;
  }

  .all-errors > .error-box { margin-top: 8px; }
"""
src = src.replace("</style>", extra_css + "\n</style>", 1)

# 3. Build the new body content (replaces everything between <body> and <script>)
new_body = r"""<body>
<div class="container">
  <header class="header">
    <div class="header-top">
      <div>
        <div class="agency-tag">Personal Finance · Quick Compare</div>
        <h1>Buy vs <em>Rent &amp; Invest</em></h1>
        <div class="hint" style="margin-top: 12px; font-size: 12px;">All parameters in one form. One button. Details collapsed by default.</div>
      </div>
      <div class="header-meta">
        <strong>Scenario</strong>
        Path A — Bought a home<br>
        Path B — Rented + invested down payment
      </div>
    </div>
  </header>

  <!-- ALL INPUTS -->
  <div class="panel">
    <div class="panel-header"><div class="icon">▸</div>All Parameters</div>
    <div class="panel-body">
      <div class="subgroup-label">Basics</div>
      <div class="form-grid">
        <div class="field">
          <label>Years to Analyze <span class="req">*</span></label>
          <input id="years" type="number" placeholder="e.g. 8" min="1" max="60">
        </div>
        <div class="field">
          <label>Loan Term <span class="req">*</span></label>
          <input id="loanYears" type="number" placeholder="e.g. 30" min="1" max="40" value="30">
        </div>
        <div class="field">
          <label>Monthly Housing Budget <span class="req">*</span></label>
          <div class="input-prefix"><span class="pfx">$</span>
            <input id="monthly" type="number" placeholder="e.g. 5500" min="1">
          </div>
        </div>
        <div class="field">
          <label>Down Payment / Investment <span class="req">*</span></label>
          <div class="input-prefix"><span class="pfx">$</span>
            <input id="downpay" type="number" placeholder="e.g. 200000" min="1">
          </div>
        </div>
        <div class="field field-full">
          <div style="display: flex; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 8px; flex-wrap: wrap;">
            <label style="margin: 0;">Stock Ticker <span class="req">*</span></label>
            <label style="display: flex; align-items: center; gap: 6px; font-size: 10px; color: var(--text-dim); margin: 0; letter-spacing: 0.05em; text-transform: none; cursor: pointer;">
              <input type="checkbox" id="useCached" style="width: auto; margin: 0;"> use cached
            </label>
          </div>
          <input id="ticker" type="text" placeholder="SPY · VTI · QQQ" maxlength="8" style="text-transform:uppercase;">
          <select id="tickerSelect" style="display: none; background: var(--bg); border: 1px solid var(--border-bright); border-radius: 1px; color: var(--text-bright); font-family: var(--mono); font-size: 14px; padding: 12px 14px; width: 100%; outline: none; letter-spacing: 0.05em;">
            <option value="VOO">VOO — Vanguard S&amp;P 500 ETF</option>
            <option value="AAPL">AAPL — Apple Inc.</option>
            <option value="GOOG">GOOG — Alphabet Inc.</option>
            <option value="QCOM">QCOM — Qualcomm Inc.</option>
            <option value="NVDA">NVDA — NVIDIA Corp.</option>
          </select>
          <span class="hint" id="cachedHint">Enable "use cached" for VOO / AAPL / GOOG / QCOM / NVDA (last 20 yr · no API key)</span>
        </div>
        <div class="field field-full" id="apiKeyWrapper">
          <label>Alpha Vantage API Key</label>
          <input id="apiKey" type="text" placeholder="paste free key (saved in browser)" autocomplete="off">
          <span class="hint">Free at <a href="https://www.alphavantage.co/support/#api-key" target="_blank">alphavantage.co</a> · 25 calls/day · skipped when "use cached" is on</span>
        </div>
      </div>

      <div class="subgroup-label">Buy &amp; Carry (CA)</div>
      <div class="form-grid">
        <div class="field">
          <label>HOA / Month</label>
          <div class="input-prefix"><span class="pfx">$</span>
            <input id="hoa" type="number" placeholder="0" min="0" value="0">
          </div>
        </div>
        <div class="field">
          <label>Mortgage Rate (APR %)</label>
          <input id="rate" type="number" placeholder="e.g. 7.0" min="0" max="30" step="0.01" value="7.0">
        </div>
        <div class="field">
          <label>Insurance Rate (% / yr)</label>
          <input id="insRate" type="number" min="0" max="5" step="0.05" value="0.35">
        </div>
        <div class="field">
          <label>Marginal Tax Rate (%)</label>
          <input id="taxRate" type="number" min="0" max="60" step="0.1" value="35">
        </div>
        <div class="field">
          <label>SALT Cap / Year ($)</label>
          <input id="saltCap" type="number" min="0" step="500" value="10000">
        </div>
      </div>

      <div class="subgroup-label">Sale</div>
      <div class="form-grid">
        <div class="field">
          <label>ZIP Code <span class="req">*</span></label>
          <input id="saleZip" type="text" maxlength="5" placeholder="e.g. 94110" inputmode="numeric">
        </div>
        <div class="field">
          <label>Sale Year <span class="req">*</span></label>
          <input id="saleYear" type="number" min="1975" max="2099" placeholder="e.g. 2025">
          <span class="hint" id="purchaseYearHint">Purchase year = sale − X</span>
        </div>
        <div class="field">
          <label>Closing Cost (%)</label>
          <input id="closingPct" type="number" min="0" max="20" step="0.1" value="5">
        </div>
        <div class="field">
          <label>Purchase Price (override)</label>
          <div class="input-prefix"><span class="pfx">$</span>
            <input id="actualPurchase" type="number" min="0" placeholder="optional">
          </div>
        </div>
        <div class="field">
          <label>Sale Price (override)</label>
          <div class="input-prefix"><span class="pfx">$</span>
            <input id="actualSale" type="number" min="0" placeholder="optional">
          </div>
        </div>
      </div>

      <div class="subgroup-label">Rent</div>
      <div class="form-grid">
        <div class="field">
          <label>Annual Rent Increase (%)</label>
          <input id="rentInc" type="number" min="0" max="30" step="0.1" value="3.5">
        </div>
        <div class="field">
          <label>Starting Monthly Rent</label>
          <div class="input-prefix"><span class="pfx">$</span>
            <input id="rentStart" type="number" min="0" placeholder="defaults to budget">
          </div>
        </div>
      </div>

      <div class="btn-row" style="margin-top: 28px;">
        <button onclick="computeAll()">Calculate All Paths ▸</button>
        <button class="secondary" onclick="resetParams()">Reset</button>
        <div class="loader-text" id="hpiLoader" style="font-size:11px;color:var(--text-dim);display:none;align-items:center;gap:8px;">
          <span style="display:inline-block;width:12px;height:12px;border:1.5px solid var(--border-bright);border-top-color:var(--amber);border-radius:50%;animation:spin 0.8s linear infinite;"></span>
          Loading HPI dataset…
        </div>
        <div class="loader-text" id="stockLoader" style="font-size:11px;color:var(--text-dim);display:none;align-items:center;gap:8px;">
          <span style="display:inline-block;width:12px;height:12px;border:1.5px solid var(--border-bright);border-top-color:var(--amber);border-radius:50%;animation:spin 0.8s linear infinite;"></span>
          Loading prices…
        </div>
      </div>

      <div class="all-errors">
        <div class="error-box" id="errorBox"></div>
        <div class="error-box" id="errorBox2"></div>
        <div class="error-box" id="errorBox3"></div>
        <div class="error-box" id="errorBox4"></div>
        <div class="error-box" id="errorBox5"></div>
        <div class="error-box" id="errorBox6"></div>
      </div>

      <!-- Hidden Step 01 stub: JS still calls into these IDs from saveParams() -->
      <div id="summary" style="display:none;">
        <span id="sumYears"></span><span id="sumLoanYears"></span><span id="sumTicker"></span><span id="sumMonthly"></span><span id="sumDownpay"></span><span id="sumTotal"></span>
      </div>
    </div>
  </div>

  <!-- TOP-LEVEL SUMMARY (always visible after compute) -->
  <div class="summary" id="compareSummary" style="margin-top: 24px;">
    <div class="panel">
      <div class="panel-header"><div class="icon">✓</div>Summary · Path A vs Path B</div>
      <div class="panel-body">
        <div class="breakdown breakdown-compare" style="margin-top: 0;">
          <div class="breakdown-row breakdown-head">
            <div>Bucket</div>
            <div class="num">Path A · Buy</div>
            <div class="num">Path B · Rent + Invest</div>
          </div>
          <div class="breakdown-row">
            <div>Cash Deployed (X yr)</div>
            <div class="num" id="cmpCashA">—</div>
            <div class="num" id="cmpCashB">—</div>
          </div>
          <div class="breakdown-row">
            <div>Housing Outflow</div>
            <div class="num" id="cmpHousingA">—</div>
            <div class="num" id="cmpHousingB">—</div>
          </div>
          <div class="breakdown-row">
            <div>Asset Value @ Year X</div>
            <div class="num" id="cmpAssetA">—</div>
            <div class="num" id="cmpAssetB">—</div>
          </div>
          <div class="breakdown-row">
            <div>+ Tax Savings</div>
            <div class="num" id="cmpTaxA">—</div>
            <div class="num" id="cmpTaxB">$0</div>
          </div>
          <div class="breakdown-row breakdown-subtotal">
            <div>Net Wealth @ Year X</div>
            <div class="num" id="cmpWealthA">—</div>
            <div class="num" id="cmpWealthB">—</div>
          </div>
          <div class="breakdown-row breakdown-total">
            <div>P&amp;L vs Cash Deployed</div>
            <div class="num" id="cmpProfitA">—</div>
            <div class="num" id="cmpProfitB">—</div>
          </div>
        </div>

        <div class="summary-grid" style="grid-template-columns: 1fr; margin-top: 24px;">
          <div class="summary-cell" style="text-align:center; padding: 28px;">
            <div class="summary-label" id="verdictLbl">VERDICT</div>
            <div class="summary-value amber" id="verdict" style="font-size: 32px;">—</div>
            <div class="result-sub" id="verdictDetail" style="font-size:12px; color:var(--text-dim); margin-top:8px;"></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- COLLAPSIBLE DETAILS -->

  <details class="detail-block">
    <summary>Buy &amp; Carry — home price, monthly decomposition, lifetime costs</summary>
    <div class="detail-content">
      <div class="summary visible" id="housingSummary">
        <div class="summary-grid" style="grid-template-columns: 2fr 1fr 1fr;">
          <div class="summary-cell">
            <div class="summary-label">Computed Max Home Price</div>
            <div class="summary-value amber" id="hHomePrice" style="font-size: 32px;">—</div>
          </div>
          <div class="summary-cell">
            <div class="summary-label">Loan Amount</div>
            <div class="summary-value" id="hLoan">—</div>
          </div>
          <div class="summary-cell">
            <div class="summary-label">Down Payment %</div>
            <div class="summary-value" id="hDownPct">—</div>
          </div>
        </div>

        <div class="breakdown">
          <div class="breakdown-row breakdown-head"><div>Monthly Decomposition</div><div>Detail</div><div class="num">$/mo</div></div>
          <div class="breakdown-row"><div>Mortgage P&amp;I</div><div class="dim" id="dPiDetail">amortized at user rate</div><div class="num" id="dPi">—</div></div>
          <div class="breakdown-row"><div>Property Tax</div><div class="dim">1% / yr ÷ 12 (Prop 13)</div><div class="num" id="dTax">—</div></div>
          <div class="breakdown-row"><div>Homeowners Insurance</div><div class="dim" id="dInsDetail">—</div><div class="num" id="dIns">—</div></div>
          <div class="breakdown-row"><div>HOA</div><div class="dim">user input</div><div class="num" id="dHoa">—</div></div>
          <div class="breakdown-row breakdown-subtotal"><div>Total Monthly (PITI + HOA)</div><div class="dim">should match budget</div><div class="num" id="dTotal">—</div></div>
        </div>

        <div class="breakdown" style="margin-top: 20px;">
          <div class="breakdown-row breakdown-head"><div>X-Year Totals</div><div>Detail</div><div class="num">Amount</div></div>
          <div class="breakdown-row"><div>Down Payment</div><div class="dim">paid year 0</div><div class="num" id="rDown">—</div></div>
          <div class="breakdown-row"><div>Monthly Payments (all-in)</div><div class="dim" id="rMonthlyDetail">—</div><div class="num" id="rMonthly">—</div></div>
          <div class="breakdown-row breakdown-subtotal"><div>Gross Cash Outflow</div><div class="dim">down + monthly × 12 × X</div><div class="num" id="rGross">—</div></div>
          <div class="breakdown-row positive"><div>− Tax Savings (CA itemized)</div><div class="dim" id="rSavingsDetail">—</div><div class="num" id="rSavings">—</div></div>
          <div class="breakdown-row breakdown-total"><div>NET TOTAL · Path A</div><div class="dim">cash truly spent on housing</div><div class="num" id="rNet">—</div></div>
        </div>

        <div class="breakdown breakdown-compare" style="margin-top: 20px;">
          <div class="breakdown-row breakdown-head">
            <div>Lifetime Cost Buckets</div>
            <div class="num" id="lifeXHead">Over X yr</div>
            <div class="num" id="lifeLHead">Over loan term</div>
          </div>
          <div class="breakdown-row"><div>Mortgage Interest</div><div class="num" id="lInterestX">—</div><div class="num" id="lInterestL">—</div></div>
          <div class="breakdown-row"><div>Mortgage Principal</div><div class="num" id="lPrincipalX">—</div><div class="num" id="lPrincipalL">—</div></div>
          <div class="breakdown-row"><div>Property Tax</div><div class="num" id="lTaxX">—</div><div class="num" id="lTaxL">—</div></div>
          <div class="breakdown-row"><div>Homeowners Insurance</div><div class="num" id="lInsX">—</div><div class="num" id="lInsL">—</div></div>
          <div class="breakdown-row"><div>HOA</div><div class="num" id="lHoaX">—</div><div class="num" id="lHoaL">—</div></div>
          <div class="breakdown-row breakdown-subtotal"><div>Total Cash Out (excl. down)</div><div class="num" id="lTotalX">—</div><div class="num" id="lTotalL">—</div></div>
        </div>

        <div class="aux-grid" style="grid-template-columns: 1fr 1fr;">
          <div class="aux-cell"><div class="aux-label">Loan Balance @ Year X</div><div class="aux-value" id="hBalance">—</div></div>
          <div class="aux-cell"><div class="aux-label">Loan Balance @ End of Term</div><div class="aux-value" id="hBalanceEnd">$0</div></div>
        </div>
      </div>
    </div>
  </details>

  <details class="detail-block">
    <summary>Sell &amp; Realize — HPI lookup, sale math, Path A P&amp;L</summary>
    <div class="detail-content">
      <div class="summary visible" id="saleSummary">
        <div class="summary-grid" style="grid-template-columns: 1fr 1fr 1fr;">
          <div class="summary-cell"><div class="summary-label" id="hpiFromLbl">HPI · Purchase Year</div><div class="summary-value" id="hpiFromVal">—</div></div>
          <div class="summary-cell"><div class="summary-label" id="hpiToLbl">HPI · Sale Year</div><div class="summary-value" id="hpiToVal">—</div></div>
          <div class="summary-cell"><div class="summary-label">HPI Ratio (sale ÷ buy)</div><div class="summary-value amber" id="hpiRatioVal">—</div></div>
        </div>

        <div class="breakdown" style="margin-top: 20px;">
          <div class="breakdown-row breakdown-head"><div>Sale Math</div><div>Detail</div><div class="num">Amount</div></div>
          <div class="breakdown-row"><div>Sale Price @ Year X</div><div class="dim" id="sSalePxDetail">home price × HPI ratio</div><div class="num" id="sSalePx">—</div></div>
          <div class="breakdown-row"><div>− Closing Costs</div><div class="dim" id="sClosingDetail">% of sale price</div><div class="num" id="sClosing">—</div></div>
          <div class="breakdown-row"><div>− Loan Balance Payoff</div><div class="dim">unamortized principal at year X</div><div class="num" id="sBalance">—</div></div>
          <div class="breakdown-row breakdown-subtotal"><div>= Net Sale Proceeds</div><div class="dim">cash in hand after closing</div><div class="num" id="sNetSale">—</div></div>
        </div>

        <div class="breakdown" style="margin-top: 20px;">
          <div class="breakdown-row breakdown-head"><div>Path A · Final P&amp;L</div><div>Detail</div><div class="num">Amount</div></div>
          <div class="breakdown-row"><div>Net Sale Proceeds</div><div class="dim">from above</div><div class="num" id="pNetSale">—</div></div>
          <div class="breakdown-row"><div>− Total Money Spent</div><div class="dim" id="pSpentDetail">down + monthly × 12 × X</div><div class="num" id="pSpent">—</div></div>
          <div class="breakdown-row positive"><div>+ Tax Savings (CA itemized)</div><div class="dim">from buy step</div><div class="num" id="pTaxSave">—</div></div>
          <div class="breakdown-row breakdown-total"><div id="pProfitLbl">PROFIT · Path A</div><div class="dim">net cash position vs not buying</div><div class="num" id="pProfit">—</div></div>
        </div>
      </div>
    </div>
  </details>

  <details class="detail-block">
    <summary>Rent — year-by-year cash outlay</summary>
    <div class="detail-content">
      <div class="summary visible" id="rentSummary">
        <div class="summary-grid" style="grid-template-columns: 1fr 1fr 1fr;">
          <div class="summary-cell"><div class="summary-label">Starting Rent</div><div class="summary-value" id="rStart">—</div></div>
          <div class="summary-cell"><div class="summary-label" id="rEndLbl">Year X Rent</div><div class="summary-value" id="rEnd">—</div></div>
          <div class="summary-cell"><div class="summary-label">Total Rent Paid</div><div class="summary-value amber" id="rTotal" style="font-size:28px;">—</div></div>
        </div>

        <div class="breakdown" style="margin-top: 20px;">
          <div class="breakdown-row breakdown-head"><div>Year</div><div>Monthly Rent</div><div class="num">Annual Total</div></div>
          <div id="rentRows"></div>
          <div class="breakdown-row breakdown-total"><div>TOTAL · X Years</div><div class="dim" id="rTotalDetail">—</div><div class="num" id="rTotalRow">—</div></div>
        </div>
      </div>
    </div>
  </details>

  <details class="detail-block">
    <summary>Stock Investment — lump-sum growth</summary>
    <div class="detail-content">
      <div class="summary visible" id="stockSummary">
        <div class="summary-grid" style="grid-template-columns: 1fr 1fr 1fr 1fr;">
          <div class="summary-cell"><div class="summary-label">Ticker</div><div class="summary-value amber" id="kTicker">—</div></div>
          <div class="summary-cell"><div class="summary-label" id="kStartLbl">Price · Buy Year</div><div class="summary-value" id="kStart">—</div></div>
          <div class="summary-cell"><div class="summary-label" id="kEndLbl">Price · Sale Year</div><div class="summary-value" id="kEnd">—</div></div>
          <div class="summary-cell"><div class="summary-label">Price Ratio</div><div class="summary-value amber" id="kRatio">—</div></div>
        </div>

        <div class="breakdown" style="margin-top: 20px;">
          <div class="breakdown-row breakdown-head"><div>Stock Math</div><div>Detail</div><div class="num">Amount</div></div>
          <div class="breakdown-row"><div>Initial Investment</div><div class="dim">down payment from inputs</div><div class="num" id="kInit">—</div></div>
          <div class="breakdown-row"><div>Shares Purchased</div><div class="dim" id="kSharesDetail">init ÷ start price</div><div class="num" id="kShares">—</div></div>
          <div class="breakdown-row breakdown-subtotal"><div>End Value @ Year X</div><div class="dim" id="kEndValueDetail">shares × end price</div><div class="num" id="kEndValue">—</div></div>
          <div class="breakdown-row breakdown-total"><div id="kProfitLbl">UNREALIZED PROFIT</div><div class="dim">end value − initial</div><div class="num" id="kProfit">—</div></div>
        </div>
      </div>
    </div>
  </details>

  <details class="detail-block">
    <summary>Year-by-Year Cashflow — Path B simulation (rent + reinvested surplus)</summary>
    <div class="detail-content">
      <div class="breakdown">
        <div class="breakdown-row breakdown-head" style="grid-template-columns: 0.6fr 0.6fr 1fr 1fr 1fr 1fr 1fr;">
          <div>y</div><div>Year</div>
          <div class="num">Rent / mo</div><div class="num">Surplus (yr)</div>
          <div class="num">Stock Px</div><div class="num">Shares</div><div class="num">Portfolio</div>
        </div>
        <div id="cmpYearRows"></div>
      </div>
    </div>
  </details>

  <div class="disclaimer">
    <strong>Sources &amp; References</strong><br>
    <span style="display: inline-block; line-height: 2;">
      Sale-price &amp; appreciation model · <a href="https://www.fhfa.gov/data/hpi/datasets?tab=hpi-calculator" target="_blank">FHFA House Price Index Calculator</a><br>
      Tax-deduction model · <a href="https://myhome.freddiemac.com/resources/calculators/tax-savings" target="_blank">Freddie Mac Tax Savings Calculator</a><br>
      Mortgage rate history · <a href="https://fred.stlouisfed.org/series/MORTGAGE30US" target="_blank">FRED 30-Yr Fixed Mortgage Average</a><br>
      Amortization / loan-balance math · <a href="https://www.bankrate.com/mortgages/amortization-calculator/" target="_blank">Bankrate Amortization Calculator</a><br>
      Home-price affordability formula · <a href="https://www.chase.com/personal/mortgage/calculators-resources/affordability-calculator" target="_blank">Chase Affordability Calculator</a>
    </span>
  </div>

  <div class="disclaimer" style="margin-top: 16px;">
    <strong>Methodology &middot; Same model as the step-by-step page</strong><br>
    Both paths receive the same annual cash budget (<em>monthly × 12</em>). Path A spends it on PITI + HOA;
    Path B pays rent and invests the surplus (or withdraws if rent exceeds budget).
    Ending wealth = sale proceeds + tax savings (Path A) or stock portfolio value (Path B).
    All numbers are <em>nominal</em> — no inflation or discount-rate adjustment.
  </div>
</div>
"""

# Replace from <body> through the line just before <script>.
# The script tag and everything after it (existing JS + </body></html>) is unchanged.
src = re.sub(
    r"<body>.*?(?=<script>)",
    new_body,
    src,
    count=1,
    flags=re.DOTALL,
)

# 4. Append computeAll() function and re-wire keyboard + page init.
# We insert just before </script>.
js_addons = r"""

// --- Quick-compare entry point ---
async function computeAll() {
  // Clear all error boxes first
  ['errorBox','errorBox2','errorBox3','errorBox4','errorBox5','errorBox6']
    .forEach(id => document.getElementById(id).classList.remove('visible'));
  document.getElementById('compareSummary').classList.remove('visible');
  await computeCompare();
}
"""
src = src.replace("</script>", js_addons + "\n</script>", 1)

DST.write_text(src, encoding="utf-8")
print(f"Wrote {DST}: {len(src):,} chars, {src.count(chr(10))+1} lines")
