# 📈 Trading Profit Management Dashboard

A comprehensive web-based dashboard for managing trading accounts, tracking profits/losses, and analyzing trading performance. Built with Streamlit and featuring modern UI, database persistence, and real-time notifications.

## 🌟 Features

- **Multi-Account Management**: Add/edit trading accounts with capital tracking
- **Advanced Trade Management**: Create trades, add positions (averaging), and exit with automatic P&L distribution
- **Smart Profit Distribution**: Automatic profit sharing based on capital contribution ratios
- **Comprehensive Analytics**: ROI tracking, performance charts, and historical analysis
- **Trade History**: Full trade history with filtering, export, and statistics
- **Modern UI**: Clean, responsive design with gradient styling and popup notifications
- **Database Persistence**: All data automatically saved with SQLite/PostgreSQL support
- **Milestone Celebrations**: Achievement notifications and progress tracking
- **Trade Deletion**: Comprehensive trade deletion with safety confirmations

## 🚀 Quick Start

### Local Development

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd trading-dashboard
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the dashboard:**
```bash
streamlit run dashboard.py
```

4. **Open in browser:**
Navigate to `http://localhost:8501`

## 🌐 Deploy to Streamlit Cloud

### Method 1: Direct Deploy (SQLite)
1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Set main file: `dashboard.py`
5. Deploy!

⚠️ **Note**: Data may be lost on app restarts with SQLite on cloud.

### Method 2: Production Deploy (PostgreSQL)

1. **Get a free PostgreSQL database:**
   - [Aiven](https://aiven.io) (Recommended)
   - [ElephantSQL](https://elephantsql.com)
   - [Supabase](https://supabase.com)

2. **Configure Streamlit Cloud secrets:**
```toml
# In Streamlit Cloud App Settings > Secrets
DATABASE_URL = "postgresql://[username]:[password]@[host]:[port]/[database]?sslmode=require"
```

3. **Deploy to Streamlit Cloud**

## 💾 Database Options

### SQLite (Default)
- ✅ No setup required
- ✅ Works locally and on Streamlit Cloud
- ❌ Data may be lost on cloud restarts

### PostgreSQL (Recommended for Production)
- ✅ Persistent storage
- ✅ Production-ready
- ✅ Free tier available

## 🛠 Technology Stack

- **Frontend**: Streamlit with custom CSS
- **Backend**: Python with pandas for data processing
- **Database**: SQLite (default) / PostgreSQL (production)
- **Visualization**: Plotly for interactive charts
- **Deployment**: Streamlit Cloud / Any Python hosting

## 📊 Core Business Logic

### Capital Management
- Proportional profit distribution based on capital contribution
- Dynamic capital share calculation
- Support for capital additions and withdrawals

### Trade Processing
- Position averaging with automatic price calculation
- Partial and full trade exits
- Fee tracking and P&L calculation
- Multi-account trade linking
- Trade deletion with safety confirmations

### Data Architecture
```
accounts (user_id, name, email, capital, profit)
trades (trade_id, symbol, qty, avg_price, strategy, accounts, status)
trade_history (trade_id, symbol, entry/exit details, profit_loss)
```

## 🎯 Key Functions

| Function | Purpose |
|----------|---------|
| `initialize_session_state()` | Load data from database into session |
| `calculate_capital_share()` | Compute profit distribution ratios |
| `update_trade_average()` | Handle position averaging math |
| `execute_trade_exit()` | Process trade closures and profit distribution |
| `delete_trade_from_db()` | Safe trade deletion from database |
| `save_*_to_db()` | Database persistence functions |

## 🎯 Key Features

- Real-time popup notifications
- 2-decimal precision throughout
- Milestone celebrations
- Professional database integration
- Multi-user support
- Data export capabilities
- Comprehensive trade deletion with safety checks

---

**Start tracking your trading success today!** 📊💰
