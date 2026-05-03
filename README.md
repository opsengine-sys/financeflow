# FinanceFlow

A modern, mobile-friendly full-stack finance management application built with Flask and SQLite. FinanceFlow provides users with comprehensive expense tracking, investment insights, AI-powered financial recommendations, and secure authentication via Clerk SSO.

## Features

### 💰 Core Financial Management
- **Smart Expense Tracking** — Categorized transactions with real-time budget monitoring
- **Income & Lending Management** — Track income sources, loans, and borrowing
- **Budget Controls** — Visual progress bars and spending alerts to stay within limits
- **Financial Goals** — Create and monitor savings goals with progress tracking

### 📊 Dashboard & Analytics
- **Real-time Dashboard** — Comprehensive overview of income, expenses, savings, and cash flow
- **Transaction History** — Detailed transaction logs with filtering and search
- **Spending Insights** — AI-powered analysis of spending patterns and recommendations
- **Smart Categorization** — Automatic transaction categorization with manual override options

### 💹 Investments & Market Pulse
- **Market Pulse** — Live ticker cards displaying market indices and crypto prices with real-time changes
- **Investment Portfolio** — Track investment holdings with performance metrics
- **Investment Management** — Add, edit, and manage individual investments
- **Market Data Integration** — Live market quotes and price updates

### 🔐 Security & Authentication
- **Clerk SSO Integration** — Secure single sign-on with email, social, and multi-factor authentication
- **JWT-based Backend** — Token-based API authentication for enhanced security
- **Session Management** — Persistent login with automatic token refresh

### 🎨 User Experience
- **Dark Mode Support** — Full dark theme for comfortable viewing in low-light environments
- **Responsive Design** — Mobile-first approach with full tablet and desktop support
- **Compact Mode** — Reduced padding and font sizes for optimal space utilization
- **Smooth Animations** — Fluid transitions and micro-interactions throughout the app

### 📱 Mobile Features
- **Bottom Navigation** — Touch-friendly navigation bar for mobile devices
- **Pull-to-Refresh** — Native-like pull-to-refresh functionality for data sync
- **Optimized Layouts** — Space-efficient card layouts for smaller screens
- **FAB Button** — Floating action button for quick transaction entry

### 📑 Export & Reporting
- **PDF Export** — Generate PDF reports of transactions and portfolio summaries
- **Data Export** — Export financial data in multiple formats for analysis
- **Historical Reports** — Archive and review past financial statements

### 🤖 AI-Powered Insights
- **Spending Analysis** — AI-generated insights on spending habits and trends
- **Finance Recommendations** — Personalized financial advice based on user data
- **Natural Language Processing** — Conversational AI for financial guidance

## Tech Stack

### Frontend
- **HTML5/CSS3** — Semantic markup with custom CSS variables for theming
- **Vanilla JavaScript** — No framework dependencies; lightweight and performant
- **Responsive Grid System** — Mobile-first CSS Grid and Flexbox layouts
- **Font Integration** — Google Fonts (Sora, DM Sans) for modern typography

### Backend
- **Flask** — Lightweight Python web framework
- **SQLite** — Embedded relational database for data persistence
- **Flask-JWT-Extended** — JWT token management for API authentication
- **Flask-CORS** — Cross-origin resource sharing for secure frontend-backend communication

### Authentication
- **Clerk** — Modern authentication platform with SSO support
- **JWT Tokens** — Stateless authentication for REST APIs

### Deployment
- **Replit** — Cloud-based development and deployment platform

## Project Structure

```
.
├── index.html              # Single-file frontend with HTML, CSS, JavaScript
├── server.py               # Flask backend with API routes and database
├── database.db             # SQLite database (auto-created)
├── replit.md               # Replit configuration and usage guide
├── pyproject.toml          # Python dependencies and project metadata
└── README.md               # This file
```

## Getting Started

### Prerequisites
- Python 3.8+
- Modern web browser with JavaScript enabled
- Clerk account for SSO setup (optional for basic usage)

### Installation

1. **Clone or open the project in Replit**
   ```bash
   git clone <repository-url>
   cd financeflow
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # or via poetry
   poetry install
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file with:
   CLERK_PUBLISHABLE_KEY=your_clerk_key
   CLERK_SECRET_KEY=your_clerk_secret
   FLASK_ENV=development
   ```

4. **Initialize the database**
   ```bash
   python server.py
   ```

5. **Open in browser**
   Navigate to `http://localhost:5000` or use Replit's preview pane

## Usage

### Dashboard
- View your financial overview on the home page
- Monitor income, expenses, savings, and cash flow in real-time
- Access AI-powered spending insights

### Transactions
- Click the FAB button (+) to add a new transaction
- Select transaction type: Expense, Income, Lending, or Borrowing
- Categorize transactions and add notes
- View detailed transaction history

### Budgets
- Set budget limits for each expense category
- Monitor progress with visual bars
- Receive alerts when approaching limits

### Goals
- Create financial savings goals
- Track progress toward each goal
- View target dates and remaining amounts

### Investments
- View live market data in Market Pulse
- Click tickers to see current prices and changes
- Add and manage investment holdings
- Track portfolio performance

### Settings
- Toggle dark mode
- Enable compact mode for reduced spacing
- Manage notification preferences
- Export data and reports

## API Endpoints

### Authentication
- `GET /api/auth/clerk-config` — Get Clerk configuration

### User Data
- `GET /api/user` — Get current user profile
- `POST /api/user/update` — Update user profile

### Financial Data
- `GET /api/data` — Get all transactions and financial summary
- `POST /api/transaction` — Create a new transaction
- `PUT /api/transaction/:id` — Update a transaction
- `DELETE /api/transaction/:id` — Delete a transaction

### Market Data
- `GET /api/market/tickers` — Get live market ticker data
- `GET /api/market/indices` — Get market indices

### AI Insights
- `POST /api/ai/insights` — Generate AI-powered financial insights

## Browser Support

- Chrome/Edge 88+
- Firefox 85+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Performance Optimization

- **Lazy Loading** — Images and heavy components load on demand
- **CSS Variables** — Theme changes without full page refresh
- **Minimal Dependencies** — No heavy frameworks; vanilla JS for speed
- **Responsive Images** — Optimized for all screen sizes
- **Caching** — Browser caching for static assets

## Customization

### Theming
Edit CSS variables in `index.html` `:root` section:
```css
:root {
  --primary: #047857;      /* Primary brand color */
  --accent: #10B981;       /* Accent color */
  --danger: #EF4444;       /* Error/danger color */
  /* ... more variables */
}
```

### Adding Categories
Edit the category list in the transaction modal to add custom expense categories.

### Modifying Layouts
All layouts use CSS Grid and Flexbox—adjust `.stats-grid`, `.card`, and other container classes.

## Security

- **HTTPS Only** — Always use HTTPS in production
- **CSRF Protection** — Implement CSRF tokens for state-changing operations
- **Input Validation** — All user inputs are validated server-side
- **Rate Limiting** — API endpoints have rate limiting enabled
- **Secure Headers** — Security headers configured for XSS/clickjacking prevention

## Troubleshooting

### White line between sidebar and content
- Check if sidebar has `box-shadow` or `border-right` styles
- Ensure `greeting-card` margins extend correctly with negative margins

### Ticker cards not aligned
- Verify flexbox properties: `display: flex; align-items: center; justify-content: space-between;`
- Check fixed widths on price and change columns

### Dark mode not working
- Ensure `.dark-mode` class is applied to `<body>` element
- Verify CSS variables are defined in `body.dark-mode` selector

### Clerk login issues
- Verify Clerk publishable key is set in environment
- Check browser console for Clerk-related errors
- Ensure Clerk domain is whitelisted in Clerk dashboard

## Contributing

To contribute improvements:
1. Create a new branch for your feature
2. Make changes and test thoroughly
3. Submit a pull request with a clear description

## License

MIT License — feel free to use and modify for personal or commercial projects.

## Support

For issues, questions, or feature requests:
- Check existing GitHub issues
- Create a new issue with detailed description
- Contact the development team via Replit

---

**Version:** 1.0.0  
**Last Updated:** May 2026  
**Built with ❤️ on Replit**
