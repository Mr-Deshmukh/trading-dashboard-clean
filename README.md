# 📈 Trading Profit Management Dashboard

A comprehensive web-based dashboard for managing trading accounts, tracking profits/losses, and analyzing trading performance.

## 🌟 Features

- **Multi-Account Management**: Add/edit trading accounts with capital tracking
- **Advanced Trade Management**: Create trades, add positions (averaging), and exit with automatic P&L distribution
- **Smart Profit Distribution**: Automatic profit sharing based on capital contribution ratios
- **Comprehensive Analytics**: ROI tracking, performance charts, and historical analysis
- **Trade History**: Full trade history with filtering, export, and statistics
- **Modern UI**: Clean, responsive design with gradient styling and popup notifications
- **Database Persistence**: PostgreSQL support for production deployment

## 🚀 Deploy to Streamlit Cloud

### Step 1: Configure Database
In Streamlit Cloud app settings → Secrets, add your PostgreSQL connection:

```toml
DATABASE_URL = "postgresql://username:password@host:port/database"
```

### Step 2: Deploy
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect this GitHub repository
3. Main file: `dashboard.py`
4. Deploy!

## 🛠 Technology Stack

- **Frontend**: Streamlit with custom CSS
- **Backend**: Python with pandas
- **Database**: PostgreSQL (production) / SQLite (local)
- **Visualization**: Plotly charts

## 💾 Local Development

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

## 🎯 Key Features

- Real-time popup notifications
- 2-decimal precision throughout
- Milestone celebrations
- Professional database integration
- Multi-user support
- Data export capabilities

---

**Start tracking your trading success today!** 📊💰