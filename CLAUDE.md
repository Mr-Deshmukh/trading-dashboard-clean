# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Trading Profit Management Dashboard** built with Streamlit. It's a single-page application that manages trading accounts, tracks profit/loss, and provides analytics for multiple users' trading activities.

### Core Architecture

The application is structured as a single-file Streamlit app (`dashboard.py`) with the following key components:

- **Database Storage**: All data persists in SQLite database (`trading_dashboard.db`)
- **Session State Management**: Data loaded from database into Streamlit's session state using pandas DataFrames
- **Three Main Data Structures**:
  - `accounts`: User accounts with capital and profit tracking
  - `trades`: Active and closed trading positions
  - `trade_history`: Historical P&L records for analytics

### Key Features

1. **Multi-Account Management**: Users can add/edit accounts with capital tracking
2. **Trade Management**: Create trades, add positions (averaging), and exit with P&L distribution
3. **Profit Distribution**: Automatic profit sharing based on capital contribution ratios
4. **Analytics Dashboard**: ROI tracking, performance charts, and historical analysis
5. **Trade History**: Comprehensive trade history with filtering, export, and statistics
6. **Modern UI**: Clean, responsive design with gradient styling and improved UX
7. **Database Persistence**: All data automatically saved to SQLite database

## Common Development Commands

```bash
# Run the application
streamlit run dashboard.py

# Install dependencies
pip install streamlit pandas numpy plotly sqlite3

# The app runs on http://localhost:8501 by default
```

## Code Architecture Notes

### Data Flow
- All data is stored in SQLite database (`trading_dashboard.db`) with automatic persistence
- Session state loads data from database on initialization
- Capital shares are calculated dynamically based on account capital ratios
- Trade averaging is handled by `update_trade_average()` function
- P&L distribution uses the `calculate_capital_share()` utility

### Key Functions
- `init_database()`: Creates SQLite database and tables
- `initialize_session_state()`: Loads data from database into session state
- `load_*_from_db()`: Database loading functions for accounts, trades, history
- `save_*_to_db()`: Database saving functions with automatic persistence
- `calculate_capital_share()`: Computes profit distribution ratios
- `update_trade_average()`: Handles position averaging math
- `execute_trade_exit()`: Processes trade closures and profit distribution

### UI Pattern
The app uses a sidebar radio button navigation system with six main pages:
- Home Dashboard (metrics and overview)
- Add/Edit Accounts
- Trade Management (add positions, exit trades)
- Analytics Dashboard
- Trade History (comprehensive history with filtering and export)

### Important Business Logic
- Profits are distributed proportionally to capital contribution
- Trades support partial exits with remaining position tracking
- All monetary values use Indian Rupees (₹) formatting
- Trade IDs are auto-generated with UUID format "TRD-XXXXXXXX"