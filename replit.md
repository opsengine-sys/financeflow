# FinanceFlow — Smart Personal Finance Tracker

A full-stack personal finance web app with real authentication, cross-device data sync, live market data, onboarding, and mobile-optimized UI.

## Stack
- **Frontend**: Pure HTML, CSS, JavaScript (no frameworks), Fonts: Sora + DM Sans
- **Backend**: Python Flask + SQLite (server.py)
- **Auth**: JWT tokens (PyJWT) + bcrypt password hashing
- **Served**: Flask on port 5000 (replaces simple http.server)

## Key Files
- `index.html` — entire frontend (~2460 lines)
- `server.py` — Flask backend (auth, CRUD APIs, market data proxy)
- `financeflow.db` — SQLite database (auto-created on first run)

## Running
Workflow: `python3 server.py` on port 5000 (webview)

## Authentication & Sync (Round 8)
- **Real sign-in / sign-up** with JWT tokens stored in localStorage
- **"Keep me signed in"** checkbox — uses localStorage (30-day) vs sessionStorage (session)
- Auto-login on return visits: checks token, fetches profile + all data
- **Cross-device sync**: every CRUD operation (add/edit/delete) is persisted to SQLite via REST API
- Sign-out clears token + resets to demo state

## Onboarding Wizard (New Users)
- 3-step wizard shown after first registration
- Step 0: Choose Quick Start (demo data) or Full Setup
- Step 1: Name, city (used for weather), monthly income
- Full Setup: prompts for primary goal + target amount
- Step 2: Confirmation screen listing all synced data types

## REST API Endpoints
- `POST /api/auth/register` — create account (name, email, password)
- `POST /api/auth/login` — sign in, returns JWT
- `GET/PUT /api/user` — profile + settings (including weatherCity)
- `GET /api/data` — fetch ALL user data in one call (used for sync on login)
- CRUD endpoints for each entity:
  - `/api/transactions`, `/api/transactions/<id>`
  - `/api/budgets`, `/api/budgets/<id>`
  - `/api/goals`, `/api/goals/<id>`
  - `/api/investments`, `/api/investments/<id>`
  - `/api/banks`, `/api/banks/<id>`
  - `/api/cards`, `/api/cards/<id>`
  - `/api/subscriptions`, `/api/subscriptions/<id>`
  - `/api/lending`, `/api/lending/<id>`
- `GET /api/market/quotes?symbols=` — Yahoo Finance proxy (live indices + stocks)
- `GET /api/market/crypto` — CoinGecko proxy (BTC + ETH in INR/USD)

## Features

### Dashboard
- Time-based greeting card with live weather (Open-Meteo)
- **Weather location**: city set in Settings → "Location & Weather" section (saved to user profile), falls back to GPS → IP → Mumbai
- **AI Insights** — dynamically computed from real data
- **Charts** — mobile-scrollable (chart-scroll wrapper), hover tooltips, ResizeObserver

### Market Pulse (Investments)
- **Fully live data** via server-side proxy (no CORS issues)
- All indices: Nifty 50 (^NSEI), Sensex (^BSESN), Nifty Bank (^NSEBANK), S&P 500, NASDAQ, Dow Jones
- Commodities: Gold, Silver, Crude Oil (Yahoo Finance futures)
- Crypto: BTC + ETH via CoinGecko
- Stocks tab: 12 Indian NSE stocks + 7 US stocks via Yahoo Finance v8

### Settings
- **Location & Weather** section: text input for city, saved to user profile + synced

## External APIs Used (all free, no API keys needed)
- Open-Meteo — weather forecast
- Nominatim (OpenStreetMap) — city geocoding + reverse geocoding
- ipapi.co — IP geolocation fallback
- CoinGecko — BTC/ETH prices in INR/USD (via server proxy)
- Yahoo Finance v8 — all stock/index/commodity prices (via server proxy)

## Python Dependencies
- flask, flask-cors, pyjwt, bcrypt, requests
