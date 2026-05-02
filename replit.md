# FinanceFlow — Smart Expense Tracker

A single-file HTML/CSS/JS personal finance tracking app.

## Stack
- Pure HTML, CSS, JavaScript (no frameworks)
- Served via `python3 -m http.server 5000`
- Fonts: Sora + DM Sans via Google Fonts

## Features (Round 4)
- **Dashboard greeting card** — time-based greeting, live weather via Open-Meteo + OpenStreetMap (no API key), rotating fun financial quotes
- **Investments page** — India (MF, Stocks, FD, PPF, EPF, NPS, Gold, SGB, Crypto) + International (US Stocks, ETFs), country filter, total/returns stats
- **Subscription detail popup** — tap any subscription to see full details modal with annual cost, renewal urgency badge, cancel button
- **Subscription renewal alerts** — alert banners for subscriptions renewing within 3 days
- **Notification bell** — header bell icon with count badge; shows budget alerts, renewal reminders, stale balance warnings
- **Budget layout** — clean flat single-row layout: icon + name + amount + progress bar + status line (no hierarchical sub-text)
- **PIN enabled status** — green "PIN is active" banner shown when PIN is set; Remove PIN button; biometric "Enabled" badge
- **Cards with full details** — credit limit, outstanding, statement day, due date, minimum payment shown in list and add form
- **Mobile hamburger menu** — top bar on mobile with ☰ button that slides sidebar open, overlay to close
- **Mobile nav customization** — Settings → Customize Bottom Tabs lets user pick exactly 4 tabs from all 8 pages
- **Settings alert toggles** — Budget Alerts, Balance Reminders, Subscription Alerts, Investment Updates as toggleable switches

## Pages
dashboard, transactions, budgets, lending, subscriptions, banks, investments, reports, settings

## Key Files
- `index.html` — entire application (~2000 lines)

## Running
Workflow: `python3 -m http.server 5000` on port 5000 (webview)
