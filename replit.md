# FinanceFlow — Smart Personal Finance Tracker

A single-file HTML/CSS/JS personal finance tracking app.

## Stack
- Pure HTML, CSS, JavaScript (no frameworks)
- Served via `python3 -m http.server 5000`
- Fonts: Sora + DM Sans via Google Fonts

## Features (current — Round 7)

### Dashboard
- Time-based greeting card with live weather (Open-Meteo)
- **Weather** — geolocation with IP-based fallback via ipapi.co (no API key required)
- **AI Insights** — dynamically computed from real transaction/budget/goal data (top spend, savings rate, budget alerts, goal progress, recurring detection)
- Dashboard stat cards with icons (Income, Expenses, Net Worth, Savings Rate)
- **Charts** — Income vs Expenses bar chart + Cash Flow Forecast line chart with hover tooltips, ResizeObserver responsive re-render, and mobile-adaptive donut chart

### Transactions
- Full-featured filter bar: search, type pills, category dropdown, sort, clear
- Fuzzy search across description, category, bank, tags
- Tap-to-detail modal (clean, no hover cards)
- CSV import with 3-step quick-start guide + download template button
- Export as CSV or JSON backup

### Market Pulse (Investments)
- Live crypto prices via CoinGecko
- **Two-tab ticker modal** — "Indices & Crypto" tab (existing 11 items) + "Stocks" tab (12 Indian NSE stocks + 7 US stocks)
- Live stock prices via Yahoo Finance API (`query2.finance.yahoo.com`) with allorigins.win CORS proxy
- Customizable with toggle chips, persisted in `selectedTickers` + `selectedStocks` Sets

### Goals & Savings, Subscriptions, Investments
- All stat cards updated with icon-header structure (stat-icon + stat-label + stat-value)

### Form Consistency
- `.period-select` matches `.form-select` (border-radius, transition, hover/focus states)
- All selects and inputs use consistent `var(--radius-md)` border radius

### Reports / CSV
- Import modal has a prominent 3-step quick-start guide with code-formatted column hints
- Template download button placed prominently above the drop zone

## Pages
dashboard, transactions, budgets, lending, subscriptions, banks, investments, reports, settings

## Key Files
- `index.html` — entire application (~2012 lines)

## Running
Workflow: `python3 -m http.server 5000` on port 5000 (webview)

## External APIs Used (all free, no keys)
- Open-Meteo — weather forecast
- ipapi.co — IP geolocation fallback for weather
- Nominatim (OpenStreetMap) — reverse geocoding for city name
- CoinGecko — live Bitcoin/Ethereum prices in INR
- Yahoo Finance v7 — live stock quotes (via allorigins.win CORS proxy)
