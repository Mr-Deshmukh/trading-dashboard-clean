# Trading Dashboard - Streamlit Cloud Deployment Guide

## 🚀 Deploying to Streamlit Cloud

### Prerequisites
1. GitHub account
2. Streamlit Cloud account (connect with GitHub)
3. This repository pushed to GitHub

### Step 1: Prepare Repository
```bash
git init
git add .
git commit -m "Initial commit: Trading Dashboard"
git remote add origin https://github.com/yourusername/trading-dashboard.git
git push -u origin main
```

### Step 2: Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your GitHub repository
4. Set main file path: `dashboard.py`
5. Click "Deploy"

## 💾 Database Options for Streamlit Cloud

### Option 1: Streamlit's Built-in Storage (Recommended for Demo)
**Pros:** 
- No setup required
- Works immediately
- Good for testing/demo

**Cons:** 
- Data may be lost on app restart
- Not suitable for production

**Setup:** No changes needed - database file will be created automatically.

### Option 2: External Database Services (Production)

#### A. Aiven (Free PostgreSQL)
```python
# Add to requirements.txt
psycopg2-binary

# Update dashboard.py database config
import psycopg2
DATABASE_URL = os.getenv('DATABASE_URL', 'your-postgresql-url')
```

#### B. PlanetScale (Free MySQL)
```python
# Add to requirements.txt  
PyMySQL

# Update dashboard.py database config
import pymysql
DATABASE_URL = os.getenv('DATABASE_URL', 'your-mysql-url')
```

#### C. MongoDB Atlas (Free)
```python
# Add to requirements.txt
pymongo

# Update dashboard.py database config
import pymongo
MONGO_URI = os.getenv('MONGO_URI', 'your-mongodb-url')
```

### Option 3: GitHub Repository as Database (Simple)
**Setup:** Store data in JSON files and commit changes back to repository.

```python
# Add to dashboard.py
import json
import requests

def save_to_github():
    # Save data as JSON to GitHub repository
    pass
```

## 🔧 Environment Variables Setup

### In Streamlit Cloud:
1. Go to your app settings
2. Click "Secrets"
3. Add your environment variables:

```toml
# .streamlit/secrets.toml
DATABASE_URL = "your-database-url"
DATABASE_PATH = "/tmp/trading_dashboard.db"
```

### Local Development:
```bash
# .env file
DATABASE_URL=your-database-url
DATABASE_PATH=./trading_dashboard.db
```

## 📁 File Structure for Deployment
```
trading-dashboard/
├── dashboard.py              # Main application
├── requirements.txt          # Dependencies
├── DEPLOYMENT.md            # This guide
├── CLAUDE.md                # Project documentation
├── setup.py                 # Setup script
├── run.sh                   # Local runner
└── .streamlit/
    ├── config.toml          # Streamlit config
    └── secrets.toml         # Environment variables (local only)
```

## 🛠 Recommended: Aiven PostgreSQL Setup (Free)

### 1. Create Aiven Account
1. Go to [aiven.io](https://aiven.io)
2. Sign up for free account
3. Create new PostgreSQL service (free tier)
4. Get connection details

### 2. Update Database Code
```python
# Add to dashboard.py
import psycopg2
from sqlalchemy import create_engine
import pandas as pd

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@host:port/db')

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def load_accounts_from_db():
    engine = create_engine(DATABASE_URL)
    try:
        df = pd.read_sql_query('''
            SELECT user_id as "User ID", name as "Name", email as "Email", 
                   capital as "Capital (₹)", profit as "Profit (₹)"
            FROM accounts
        ''', engine)
        return df
    except:
        return pd.DataFrame(columns=['User ID', 'Name', 'Email', 'Capital (₹)', 'Profit (₹)'])
```

### 3. Add to requirements.txt
```
psycopg2-binary>=2.9.0
sqlalchemy>=1.4.0
```

### 4. Set Environment Variable
In Streamlit Cloud secrets:
```toml
DATABASE_URL = "postgresql://user:password@host:port/database"
```

## 🎯 Quick Deploy (Current SQLite Version)

For immediate deployment with current SQLite setup:

1. **Push to GitHub:**
```bash
git add .
git commit -m "Trading dashboard ready for deployment"
git push origin main
```

2. **Deploy on Streamlit Cloud:**
   - Repository: `your-repo-url`
   - Branch: `main`
   - Main file path: `dashboard.py`

3. **Database will be created automatically** in the app's temporary storage.

⚠️ **Note:** With SQLite on Streamlit Cloud, data may be lost on app restarts. For persistent data, use one of the external database options above.

## 📞 Support

If you encounter issues:
1. Check Streamlit Cloud logs
2. Verify all dependencies in requirements.txt
3. Ensure database connection variables are set
4. Test locally first with `streamlit run dashboard.py`

## 🔄 Auto-Migration Script

For moving from SQLite to PostgreSQL:

```python
# migration.py
def migrate_sqlite_to_postgresql():
    # Read from SQLite
    sqlite_conn = sqlite3.connect('trading_dashboard.db')
    accounts = pd.read_sql_query("SELECT * FROM accounts", sqlite_conn)
    trades = pd.read_sql_query("SELECT * FROM trades", sqlite_conn)
    history = pd.read_sql_query("SELECT * FROM trade_history", sqlite_conn)
    
    # Write to PostgreSQL
    engine = create_engine(DATABASE_URL)
    accounts.to_sql('accounts', engine, if_exists='replace', index=False)
    trades.to_sql('trades', engine, if_exists='replace', index=False)
    history.to_sql('trade_history', engine, if_exists='replace', index=False)
```

Happy Trading! 📈