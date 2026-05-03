# FinanceFlow — Smart Personal Finance Tracker

A full-stack personal finance web app with real authentication, cross-device data sync, live market data, AI-powered insights, onboarding, and mobile-optimized UI.

## Stack
- **Frontend**: Pure HTML, CSS, JavaScript (no frameworks), Fonts: Sora + DM Sans
- **Backend**: Python Flask + SQLite (server.py)
- **Auth**: JWT tokens (PyJWT) + bcrypt password hashing + Clerk SSO (Google/Apple)
- **AI**: Replit AI Integrations → OpenAI (gpt-5-mini) for financial insights
- **Served**: Flask on port 5000

## Key Files
- `index.html` — entire frontend (~3293 lines, all CSS+JS inline)
- `server.py` — Flask backend (auth, CRUD APIs, market proxy, AI insights endpoint)
- `financeflow.db` — SQLite database (auto-created on first run)

## Running
Workflow: `python3 server.py` on port 5000 (webview)

## Authentication & Sync
- **Real sign-in / sign-up** with JWT tokens stored in localStorage
- **"Keep me signed in"** checkbox — localStorage (30-day) vs sessionStorage (session)
- Auto-login on return visits: checks token, fetches profile + all data
- **Cross-device sync**: every CRUD operation persisted to SQLite via REST API
- **Clerk SSO**: Google + Apple OAuth via Clerk v4 browser bundle
- Sign-out clears token + resets to demo state

## Onboarding Wizard (New Users)
- 3-step wizard shown after first registration
- Step 0: Quick Start (demo data) or Full Setup
- Step 1: Name, city, monthly income
- Step 2: Confirmation screen

## REST API Endpoints
- `POST /api/auth/register` — create account
- `POST /api/auth/login` — sign in, returns JWT
- `GET/PUT /api/user` — profile + settings
- `GET /api/data` — fetch ALL user data (sync on login)
- CRUD: `/api/transactions`, `/api/budgets`, `/api/goals`, `/api/investments`,
        `/api/banks`, `/api/cards`, `/api/subscriptions`, `/api/lending`
- `GET  /api/market/quotes?symbols=` — Yahoo Finance proxy (live indices + stocks)
- `GET  /api/market/crypto` — CoinGecko `/coins/markets` proxy (BTC + ETH, real 24h % change)
- `POST /api/ai/insights` — AI-powered financial insights (OpenAI via Replit AI Integrations)

## AI Insights (Dashboard — "Month in Review")
- **Real LLM**: `gpt-5-mini` via Replit AI Integrations (no API key needed, billed to Replit credits)
- Client POSTs full financial snapshot (transactions, budgets, goals, subscriptions, banks, cards)
- Server builds a concise text prompt and calls OpenAI Chat Completions with JSON mode
- Response: `{summary: "<HTML>", insights: [{icon, text}, ...]}` — rendered directly into the dashboard
- **Fallback**: if AI call fails or budget is exceeded, the original rule-based JS summary renders instead
- Badge shows "N AI insights" or falls back gracefully

## Features

### Dashboard
- Time-based greeting card with live weather (Open-Meteo)
- Weather location: city in Settings, falls back to GPS → IP → Mumbai
- **AI Insights** — real LLM analysis (gpt-5-mini) with rule-based fallback
- Charts: mobile-scrollable, hover tooltips, ResizeObserver + orientationchange resize

### Market Pulse (Investments Page)
- **Fully live data** via server-side proxy (no CORS)
- Indices: Nifty 50, Sensex, Nifty Bank, S&P 500, NASDAQ, Dow Jones (Yahoo Finance)
- Commodities: Gold, Silver, Crude Oil (Yahoo Finance futures)
- Crypto: BTC + ETH via CoinGecko `/coins/markets` (real 24h % change)
- Stocks: 12 Indian NSE + 7 US stocks
- No random jitter — only live API data shown

### Mobile UX
- 4 breakpoints: ≤1024 / ≤768 / ≤480 / ≤375px
- Sidebar: iOS-compatible scroll (`-webkit-overflow-scrolling:touch`, `100dvh`, `padding-bottom:5rem`)
- Pull-to-refresh: swipe down from top (≥72px) re-renders active page + fetches live market data
- Bottom nav, icon-only buttons, chart scroll wrappers

## External APIs
- Open-Meteo — weather
- Nominatim (OpenStreetMap) — geocoding
- ipapi.co — IP geolocation fallback
- CoinGecko — crypto prices + 24h change (server proxy)
- Yahoo Finance v8 — stocks/indices/commodities (server proxy)
- OpenAI via Replit AI Integrations — financial insights

## Python Dependencies
- flask, flask-cors, pyjwt, bcrypt, requests, openai
