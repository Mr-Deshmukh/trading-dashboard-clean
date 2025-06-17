import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import uuid
from typing import Dict, List, Any
import warnings
import sqlite3
import os
try:
    import psycopg2
    from sqlalchemy import create_engine, text
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Trading Profit Manager",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stMetric > div {
        color: white !important;
    }
    .stMetric label {
        color: rgba(255, 255, 255, 0.8) !important;
    }
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    .stNumberInput > div > div > input {
        border-radius: 8px;
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
    }
    h1, h2, h3 {
        color: #2c3e50;
        font-weight: 600;
    }
    .trade-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')
DB_FILE = os.getenv('DATABASE_PATH', 'trading_dashboard.db')
USE_POSTGRESQL = DATABASE_URL is not None and POSTGRESQL_AVAILABLE

# Database functions
def init_postgresql_database():
    """Initialize PostgreSQL database with required tables"""
    if not USE_POSTGRESQL:
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Create accounts table
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS accounts (
                    user_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    capital DECIMAL(15,2) NOT NULL DEFAULT 0,
                    profit DECIMAL(15,2) NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            
            # Create trades table
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS trades (
                    trade_id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    qty INTEGER NOT NULL,
                    avg_price DECIMAL(10,2) NOT NULL,
                    strategy TEXT NOT NULL,
                    total_fees DECIMAL(10,2) DEFAULT 0,
                    date DATE NOT NULL,
                    accounts TEXT NOT NULL,
                    status TEXT DEFAULT 'Active',
                    positions TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            
            # Create trade_history table
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS trade_history (
                    id SERIAL PRIMARY KEY,
                    trade_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    entry_qty INTEGER NOT NULL,
                    entry_price DECIMAL(10,2) NOT NULL,
                    exit_qty INTEGER NOT NULL,
                    exit_price DECIMAL(10,2) NOT NULL,
                    profit_loss DECIMAL(15,2) NOT NULL,
                    date DATE NOT NULL,
                    accounts TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            
            conn.commit()
        
        st.toast("🐘 Connected to PostgreSQL database successfully!", icon="🐘")
        return True
        
    except Exception as e:
        st.error(f"PostgreSQL initialization failed: {str(e)}")
        return False

def init_database():
    """Initialize SQLite database with required tables"""
    try:
        # Ensure directory exists for database file
        db_dir = os.path.dirname(DB_FILE) if os.path.dirname(DB_FILE) else '.'
        os.makedirs(db_dir, exist_ok=True)
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Create accounts table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            capital REAL NOT NULL DEFAULT 0,
            profit REAL NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create trades table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            trade_id TEXT PRIMARY KEY,
            symbol TEXT NOT NULL,
            qty INTEGER NOT NULL,
            avg_price REAL NOT NULL,
            strategy TEXT NOT NULL,
            total_fees REAL DEFAULT 0,
            date DATE NOT NULL,
            accounts TEXT NOT NULL,
            status TEXT DEFAULT 'Active',
            positions TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create trade_history table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_id TEXT NOT NULL,
            symbol TEXT NOT NULL,
            entry_qty INTEGER NOT NULL,
            entry_price REAL NOT NULL,
            exit_qty INTEGER NOT NULL,
            exit_price REAL NOT NULL,
            profit_loss REAL NOT NULL,
            date DATE NOT NULL,
            accounts TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database initialization failed: {str(e)}")
        return False

def load_accounts_from_db():
    """Load accounts from database"""
    if USE_POSTGRESQL:
        try:
            engine = create_engine(DATABASE_URL)
            df = pd.read_sql_query('''
                SELECT user_id as "User ID", name as "Name", email as "Email", 
                       capital as "Capital (₹)", profit as "Profit (₹)"
                FROM accounts
            ''', engine)
            return df
        except:
            return pd.DataFrame(columns=['User ID', 'Name', 'Email', 'Capital (₹)', 'Profit (₹)'])
    else:
        conn = sqlite3.connect(DB_FILE)
        try:
            df = pd.read_sql_query('''
                SELECT user_id as "User ID", name as "Name", email as "Email", 
                       capital as "Capital (₹)", profit as "Profit (₹)"
                FROM accounts
            ''', conn)
            return df
        except:
            return pd.DataFrame(columns=['User ID', 'Name', 'Email', 'Capital (₹)', 'Profit (₹)'])
        finally:
            conn.close()

def load_trades_from_db():
    """Load trades from database"""
    conn = sqlite3.connect(DB_FILE)
    try:
        df = pd.read_sql_query('''
            SELECT trade_id as "Trade ID", symbol as "Symbol", qty as "Qty",
                   avg_price as "Avg Price", strategy as "Strategy",
                   total_fees as "Total Fees", date as "Date",
                   accounts as "Accounts", status as "Status", positions as "Positions"
            FROM trades
        ''', conn)
        return df
    except:
        return pd.DataFrame(columns=[
            'Trade ID', 'Symbol', 'Qty', 'Avg Price', 'Strategy', 
            'Total Fees', 'Date', 'Accounts', 'Status', 'Positions'
        ])
    finally:
        conn.close()

def load_trade_history_from_db():
    """Load trade history from database"""
    conn = sqlite3.connect(DB_FILE)
    try:
        df = pd.read_sql_query('''
            SELECT trade_id as "Trade ID", symbol as "Symbol", 
                   entry_qty as "Entry Qty", entry_price as "Entry Price",
                   exit_qty as "Exit Qty", exit_price as "Exit Price",
                   profit_loss as "Profit/Loss", date as "Date", accounts as "Accounts"
            FROM trade_history
            ORDER BY date DESC
        ''', conn)
        return df
    except:
        return pd.DataFrame(columns=[
            'Trade ID', 'Symbol', 'Entry Qty', 'Entry Price', 'Exit Qty', 
            'Exit Price', 'Profit/Loss', 'Date', 'Accounts'
        ])
    finally:
        conn.close()

def save_account_to_db(user_id, name, email, capital, profit=0):
    """Save account to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO accounts (user_id, name, email, capital, profit)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, name, email, capital, profit))
    conn.commit()
    conn.close()

def update_account_capital(user_id, new_capital):
    """Update account capital in database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE accounts SET capital = ? WHERE user_id = ?', (new_capital, user_id))
    conn.commit()
    conn.close()

def update_account_profit(user_id, profit_change):
    """Add profit to account in database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE accounts SET profit = profit + ? WHERE user_id = ?', (profit_change, user_id))
    conn.commit()
    conn.close()

def delete_account_from_db(user_id):
    """Delete account from database with proper error handling"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Check if account exists
        cursor.execute('SELECT COUNT(*) FROM accounts WHERE user_id = ?', (user_id,))
        if cursor.fetchone()[0] == 0:
            raise ValueError(f"Account {user_id} not found")
        
        # Check for related trades
        cursor.execute('SELECT COUNT(*) FROM trades WHERE accounts LIKE ?', (f'%{user_id}%',))
        trade_count = cursor.fetchone()[0]
        
        # Check for related trade history
        cursor.execute('SELECT COUNT(*) FROM trade_history WHERE accounts LIKE ?', (f'%{user_id}%',))
        history_count = cursor.fetchone()[0]
        
        if trade_count > 0 or history_count > 0:
            raise ValueError(f"Cannot delete account {user_id}: {trade_count} active trades and {history_count} history records exist. Please exit/delete trades first.")
        
        # Safe to delete
        cursor.execute('DELETE FROM accounts WHERE user_id = ?', (user_id,))
        
        if cursor.rowcount == 0:
            raise ValueError(f"Failed to delete account {user_id}")
            
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def save_trade_to_db(trade_data):
    """Save trade to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO trades 
        (trade_id, symbol, qty, avg_price, strategy, total_fees, date, accounts, status, positions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        trade_data['Trade ID'], trade_data['Symbol'], trade_data['Qty'],
        trade_data['Avg Price'], trade_data['Strategy'], trade_data['Total Fees'],
        trade_data['Date'], trade_data['Accounts'], trade_data['Status'], trade_data['Positions']
    ))
    conn.commit()
    conn.close()

def update_trade_in_db(trade_id, **kwargs):
    """Update trade in database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    for key, value in kwargs.items():
        column_map = {
            'Qty': 'qty', 'Avg Price': 'avg_price', 'Total Fees': 'total_fees',
            'Status': 'status', 'Positions': 'positions'
        }
        column = column_map.get(key, key.lower())
        cursor.execute(f'UPDATE trades SET {column} = ? WHERE trade_id = ?', (value, trade_id))
    
    conn.commit()
    conn.close()

def save_trade_history_to_db(history_data):
    """Save trade history to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trade_history 
        (trade_id, symbol, entry_qty, entry_price, exit_qty, exit_price, profit_loss, date, accounts)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        history_data['Trade ID'], history_data['Symbol'], history_data['Entry Qty'],
        history_data['Entry Price'], history_data['Exit Qty'], history_data['Exit Price'],
        history_data['Profit/Loss'], history_data['Date'], history_data['Accounts']
    ))
    conn.commit()
    conn.close()

def delete_trade_from_db(trade_id):
    """Delete trade from database with error handling"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM trades WHERE trade_id = ?', (trade_id,))
        if cursor.rowcount == 0:
            raise ValueError(f"Trade {trade_id} not found")
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def delete_trade_history_from_db(trade_id):
    """Delete trade history entries for a specific trade with error handling"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM trade_history WHERE trade_id = ?', (trade_id,))
        # Note: rowcount can be 0 if no history exists, this is not an error
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# Initialize session state
def initialize_session_state():
    # Initialize database (PostgreSQL if available, otherwise SQLite)
    if USE_POSTGRESQL:
        init_postgresql_database()
    else:
        init_database()
    
    # Load data from database
    if 'accounts' not in st.session_state:
        st.session_state.accounts = load_accounts_from_db()
    
    if 'trades' not in st.session_state:
        st.session_state.trades = load_trades_from_db()
    
    if 'trade_history' not in st.session_state:
        st.session_state.trade_history = load_trade_history_from_db()
    
    # Show welcome message on first load
    if 'app_initialized' not in st.session_state:
        st.session_state.app_initialized = True
        # Don't show popup on every refresh, only on true first load

# Utility functions
def generate_trade_id():
    return f"TRD-{str(uuid.uuid4())[:8].upper()}"

def validate_email(email):
    return "@" in email and "." in email

def calculate_capital_share(accounts_df, selected_accounts):
    if accounts_df.empty or not selected_accounts:
        return {}
    
    total_capital = accounts_df[accounts_df['User ID'].isin(selected_accounts)]['Capital (₹)'].sum()
    shares = {}
    for account in selected_accounts:
        account_capital = accounts_df[accounts_df['User ID'] == account]['Capital (₹)'].iloc[0]
        shares[account] = account_capital / total_capital if total_capital > 0 else 0
    return shares

def update_trade_average(current_qty, current_price, new_qty, new_price, current_fees, new_fees):
    total_qty = current_qty + new_qty
    total_cost = (current_qty * current_price) + (new_qty * new_price)
    avg_price = round(total_cost / total_qty, 2) if total_qty > 0 else 0.00
    total_fees = round(current_fees + new_fees, 2)
    return total_qty, avg_price, total_fees

# Main application
def main():
    initialize_session_state()
    
    st.title("📈 Trading Profit Management Dashboard")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("🔗 Navigation")
    page = st.sidebar.radio(
        "Choose a page:",
        ["🏠 Home", "➕ Add Accounts", "🛠️ Edit Accounts", "📈 Add Trades", "📊 Analytics", "📚 Trade History"]
    )
    
    if page == "🏠 Home":
        home_dashboard()
    elif page == "➕ Add Accounts":
        add_accounts()
    elif page == "🛠️ Edit Accounts":
        edit_accounts()
    elif page == "📈 Add Trades":
        add_trades()
    elif page == "📊 Analytics":
        analytics_dashboard()
    elif page == "📚 Trade History":
        trade_history_dashboard()

def home_dashboard():
    st.header("🏠 Home Dashboard")
    
    if st.session_state.accounts.empty:
        st.warning("No accounts found. Please add accounts first.")
        return
    
    # Calculate metrics
    accounts_df = st.session_state.accounts.copy()
    accounts_df['Total Value (₹)'] = accounts_df['Capital (₹)'] + accounts_df['Profit (₹)']
    total_capital = accounts_df['Capital (₹)'].sum()
    total_profit = accounts_df['Profit (₹)'].sum()
    total_value = accounts_df['Total Value (₹)'].sum()
    
    # Calculate capital share percentages
    if total_capital > 0:
        accounts_df['Capital Share (%)'] = (accounts_df['Capital (₹)'] / total_capital * 100).round(2)
    else:
        accounts_df['Capital Share (%)'] = 0
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Capital Pool", f"₹{total_capital:.2f}")
    with col2:
        st.metric("Total Profit", f"₹{total_profit:.2f}", delta=f"{(total_profit/total_capital*100):.2f}%" if total_capital > 0 else "0.00%")
    with col3:
        st.metric("Total Value", f"₹{total_value:.2f}")
    with col4:
        roi = (total_profit / total_capital * 100) if total_capital > 0 else 0
        st.metric("Overall ROI", f"{roi:.2f}%")
    
    # Check for milestones and show celebrations
    if 'last_total_profit' not in st.session_state:
        st.session_state.last_total_profit = 0
    
    # Milestone celebrations
    if total_profit > st.session_state.last_total_profit:
        if total_profit >= 100000 and st.session_state.last_total_profit < 100000:
            st.toast("🎊 Milestone Achieved: ₹1,00,000+ Total Profit!", icon="🎊")
            st.balloons()
        elif total_profit >= 50000 and st.session_state.last_total_profit < 50000:
            st.toast("🎉 Milestone Achieved: ₹50,000+ Total Profit!", icon="🎉")
            st.balloons()
        elif total_profit >= 10000 and st.session_state.last_total_profit < 10000:
            st.toast("🚀 Milestone Achieved: ₹10,000+ Total Profit!", icon="🚀")
        elif total_profit >= 1000 and st.session_state.last_total_profit < 1000:
            st.toast("💪 First ₹1,000 in Profit! Great start!", icon="💪")
    
    st.session_state.last_total_profit = total_profit
    
    st.markdown("---")
    
    # Accounts table with color coding
    st.subheader("📋 Accounts Overview")
    
    if not accounts_df.empty:
        # Style the dataframe
        def color_profit(val):
            if val > 0:
                return 'background-color: #d4edda; color: #155724'
            elif val < 0:
                return 'background-color: #f8d7da; color: #721c24'
            return ''
        
        styled_df = accounts_df.style.applymap(color_profit, subset=['Profit (₹)'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Visual charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Capital distribution pie chart
            fig_capital = px.pie(
                accounts_df, 
                values='Capital (₹)', 
                names='Name',
                title="Capital Distribution"
            )
            st.plotly_chart(fig_capital, use_container_width=True)
        
        with col2:
            # Profit by account bar chart
            fig_profit = px.bar(
                accounts_df, 
                x='Name', 
                y='Profit (₹)',
                title="Profit by Account",
                color='Profit (₹)',
                color_continuous_scale=['red', 'yellow', 'green']
            )
            st.plotly_chart(fig_profit, use_container_width=True)

def add_accounts():
    st.header("➕ Add New Account")
    
    with st.form("add_account_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name *")
            email = st.text_input("Email *")
        
        with col2:
            user_id = st.text_input("User ID *")
            initial_capital = st.number_input("Initial Capital (₹) *", min_value=0.00, value=0.00, step=0.01, format="%.2f")
        
        submitted = st.form_submit_button("Add Account")
        
        if submitted:
            # Validation
            errors = []
            
            if not name.strip():
                errors.append("Full name is required")
            if not email.strip():
                errors.append("Email is required")
            elif not validate_email(email):
                errors.append("Invalid email format")
            if not user_id.strip():
                errors.append("User ID is required")
            if initial_capital < 0:
                errors.append("Initial capital cannot be negative")
            
            # Check for duplicates
            if not st.session_state.accounts.empty:
                if user_id in st.session_state.accounts['User ID'].values:
                    errors.append("User ID already exists")
                if email in st.session_state.accounts['Email'].values:
                    errors.append("Email already exists")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Add account to database and session state
                save_account_to_db(user_id, name, email, round(initial_capital, 2), 0.00)
                
                new_account = pd.DataFrame({
                    'User ID': [user_id],
                    'Name': [name],
                    'Email': [email],
                    'Capital (₹)': [round(initial_capital, 2)],
                    'Profit (₹)': [0.00]
                })
                
                st.session_state.accounts = pd.concat([st.session_state.accounts, new_account], ignore_index=True)
                st.success(f"✅ Account for {name} added successfully!")
                st.toast(f"🎉 New account created: {name} with ₹{initial_capital:.2f} capital!", icon="🎉")
                st.balloons()
                st.rerun()

def edit_accounts():
    st.header("🛠️ Edit Accounts")
    
    if st.session_state.accounts.empty:
        st.warning("No accounts found. Please add accounts first.")
        return
    
    # Account selection
    selected_user_id = st.selectbox(
        "Select Account to Edit:",
        st.session_state.accounts['User ID'].tolist()
    )
    
    if selected_user_id:
        account_data = st.session_state.accounts[st.session_state.accounts['User ID'] == selected_user_id].iloc[0]
        
        st.subheader(f"Editing: {account_data['Name']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Current Capital:** ₹{account_data['Capital (₹)']:.2f}")
            st.info(f"**Current Profit:** ₹{account_data['Profit (₹)']:.2f}")
        
        with col2:
            st.info(f"**Email:** {account_data['Email']}")
            total_value = account_data['Capital (₹)'] + account_data['Profit (₹)']
            st.info(f"**Total Value:** ₹{total_value:.2f}")
        
        st.markdown("---")
        
        # Operations
        operation = st.radio("Select Operation:", ["💸 Add Capital", "🧾 Withdraw Capital", "🗑️ Delete Account"])
        
        if operation == "💸 Add Capital":
            with st.form("add_capital_form"):
                amount = st.number_input("Amount to Add (₹):", min_value=0.01, value=1000.00, step=0.01, format="%.2f")
                submitted = st.form_submit_button("Add Capital")
                
                if submitted:
                    new_capital = round(account_data['Capital (₹)'] + amount, 2)
                    update_account_capital(selected_user_id, new_capital)
                    
                    st.session_state.accounts.loc[
                        st.session_state.accounts['User ID'] == selected_user_id, 'Capital (₹)'
                    ] = new_capital
                    st.success(f"✅ Added ₹{amount:.2f} to {account_data['Name']}'s account!")
                    st.toast(f"💰 Capital Added: ₹{amount:.2f} to {account_data['Name']}", icon="💰")
                    st.rerun()
        
        elif operation == "🧾 Withdraw Capital":
            with st.form("withdraw_capital_form"):
                max_withdraw = account_data['Capital (₹)']
                amount = st.number_input(
                    f"Amount to Withdraw (₹) - Max: ₹{max_withdraw:.2f}:", 
                    min_value=0.01, 
                    max_value=max_withdraw,
                    value=min(1000.00, max_withdraw) if max_withdraw > 0 else 0.00,
                    step=0.01,
                    format="%.2f"
                )
                submitted = st.form_submit_button("Withdraw Capital")
                
                if submitted:
                    if amount > max_withdraw:
                        st.error("❌ Withdrawal amount exceeds available capital!")
                    else:
                        new_capital = round(account_data['Capital (₹)'] - amount, 2)
                        update_account_capital(selected_user_id, new_capital)
                        
                        st.session_state.accounts.loc[
                            st.session_state.accounts['User ID'] == selected_user_id, 'Capital (₹)'
                        ] = new_capital
                        st.success(f"✅ Withdrew ₹{amount:.2f} from {account_data['Name']}'s account!")
                        st.toast(f"🏦 Capital Withdrawn: ₹{amount:.2f} from {account_data['Name']}", icon="🏦")
                        st.rerun()
        
        elif operation == "🗑️ Delete Account":
            st.warning("⚠️ This action cannot be undone!")
            confirm = st.checkbox("I confirm I want to delete this account")
            
            if st.button("Delete Account", type="primary") and confirm:
                try:
                    delete_account_from_db(selected_user_id)
                    
                    st.session_state.accounts = st.session_state.accounts[
                        st.session_state.accounts['User ID'] != selected_user_id
                    ]
                    st.success(f"✅ Account for {account_data['Name']} deleted successfully!")
                    st.toast(f"🗑️ Account Deleted: {account_data['Name']} removed from system", icon="🗑️")
                    st.rerun()
                    
                except ValueError as e:
                    st.error(f"❌ Cannot delete account: {str(e)}")
                    st.info("💡 **Tip**: Exit or delete all trades for this account first, then try again.")
                except Exception as e:
                    st.error(f"❌ Database error: {str(e)}")
                    st.error("Please try again or contact support.")

def add_trades():
    st.header("📈 Trade Management")
    
    if st.session_state.accounts.empty:
        st.warning("No accounts found. Please add accounts first.")
        return
    
    # Trade operations
    operation = st.radio("Select Operation:", ["➕ New Trade", "📊 Add Position", "❌ Exit Trade", "🗑️ Delete Trade"])
    
    if operation == "➕ New Trade":
        new_trade_form()
    elif operation == "📊 Add Position":
        add_position_form()
    elif operation == "❌ Exit Trade":
        exit_trade_form()
    elif operation == "🗑️ Delete Trade":
        delete_trade_form()
    
    # Display active trades
    st.markdown("---")
    st.subheader("🔄 Active Trades")
    
    if not st.session_state.trades.empty:
        active_trades = st.session_state.trades[st.session_state.trades['Status'] == 'Active'].copy()
        if not active_trades.empty:
            # Display simplified view
            display_trades = active_trades[['Trade ID', 'Symbol', 'Qty', 'Avg Price', 'Strategy', 'Date']].copy()
            st.dataframe(display_trades, use_container_width=True)
        else:
            st.info("No active trades found.")
    else:
        st.info("No trades found.")

def new_trade_form():
    st.subheader("➕ Create New Trade")
    
    with st.form("new_trade_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            symbol = st.text_input("Symbol (e.g., GOLDPETAL) *")
            quantity = st.number_input("Quantity *", min_value=1, value=1)
            price = st.number_input("Price per Unit (₹) *", min_value=0.01, value=100.00, step=0.01, format="%.2f")
        
        with col2:
            strategy = st.text_input("Strategy Name *")
            fees = st.number_input("Fees (₹)", min_value=0.00, value=0.00, step=0.01, format="%.2f")
            trade_date = st.date_input("Trade Date", value=date.today())
        
        # Account selection
        accounts = st.multiselect(
            "Select Linked Accounts *",
            st.session_state.accounts['User ID'].tolist(),
            format_func=lambda x: f"{x} - {st.session_state.accounts[st.session_state.accounts['User ID']==x]['Name'].iloc[0]}"
        )
        
        submitted = st.form_submit_button("Create Trade")
        
        if submitted:
            errors = []
            
            if not symbol.strip():
                errors.append("Symbol is required")
            if not strategy.strip():
                errors.append("Strategy name is required")
            if not accounts:
                errors.append("At least one account must be selected")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                trade_id = generate_trade_id()
                trade_data = {
                    'Trade ID': trade_id,
                    'Symbol': symbol.upper(),
                    'Qty': quantity,
                    'Avg Price': round(price, 2),
                    'Strategy': strategy,
                    'Total Fees': round(fees, 2),
                    'Date': trade_date,
                    'Accounts': ','.join(accounts),
                    'Status': 'Active',
                    'Positions': f"{quantity}@{price:.2f}"
                }
                
                save_trade_to_db(trade_data)
                
                new_trade = pd.DataFrame([trade_data])
                st.session_state.trades = pd.concat([st.session_state.trades, new_trade], ignore_index=True)
                st.success(f"✅ Trade {trade_id} created successfully!")
                st.toast(f"📈 New Trade Created: {symbol.upper()} ({quantity} @ ₹{price:.2f})", icon="📈")
                st.balloons()
                st.rerun()

def add_position_form():
    st.subheader("📊 Add Position to Existing Trade")
    
    active_trades = st.session_state.trades[st.session_state.trades['Status'] == 'Active']
    
    if active_trades.empty:
        st.warning("No active trades found.")
        return
    
    trade_id = st.selectbox(
        "Select Trade:",
        active_trades['Trade ID'].tolist(),
        format_func=lambda x: f"{x} - {active_trades[active_trades['Trade ID']==x]['Symbol'].iloc[0]}"
    )
    
    if trade_id:
        trade_data = active_trades[active_trades['Trade ID'] == trade_id].iloc[0]
        
        st.info(f"**Current Position:** {trade_data['Qty']} @ ₹{trade_data['Avg Price']:.2f}")
        
        with st.form("add_position_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_qty = st.number_input("Additional Quantity *", min_value=1, value=1)
                new_price = st.number_input("Price per Unit (₹) *", min_value=0.01, value=100.00, step=0.01, format="%.2f")
            
            with col2:
                new_fees = st.number_input("Additional Fees (₹)", min_value=0.00, value=0.00, step=0.01, format="%.2f")
            
            submitted = st.form_submit_button("Add Position")
            
            if submitted:
                # Update trade with new average
                current_qty = trade_data['Qty']
                current_price = trade_data['Avg Price']
                current_fees = trade_data['Total Fees']
                
                total_qty, avg_price, total_fees = update_trade_average(
                    current_qty, current_price, new_qty, new_price, current_fees, new_fees
                )
                
                # Update positions string
                current_positions = trade_data['Positions']
                new_positions = f"{current_positions};{new_qty}@{new_price}"
                
                # Update the trade in database
                update_trade_in_db(trade_id, **{
                    'Qty': total_qty,
                    'Avg Price': avg_price,
                    'Total Fees': total_fees,
                    'Positions': new_positions
                })
                
                # Update the trade in session state
                st.session_state.trades.loc[
                    st.session_state.trades['Trade ID'] == trade_id, 
                    ['Qty', 'Avg Price', 'Total Fees', 'Positions']
                ] = [total_qty, avg_price, total_fees, new_positions]
                
                st.success(f"✅ Position added! New average: {total_qty} @ ₹{avg_price:.2f}")
                st.toast(f"📊 Position Added: +{new_qty} to {trade_data['Symbol']} (Avg: ₹{avg_price:.2f})", icon="📊")
                st.rerun()

def exit_trade_form():
    st.subheader("❌ Exit Trade")
    
    active_trades = st.session_state.trades[st.session_state.trades['Status'] == 'Active']
    
    if active_trades.empty:
        st.warning("No active trades found.")
        return
    
    trade_id = st.selectbox(
        "Select Trade to Exit:",
        active_trades['Trade ID'].tolist(),
        format_func=lambda x: f"{x} - {active_trades[active_trades['Trade ID']==x]['Symbol'].iloc[0]}"
    )
    
    if trade_id:
        trade_data = active_trades[active_trades['Trade ID'] == trade_id].iloc[0]
        
        st.info(f"**Current Position:** {trade_data['Qty']} @ ₹{trade_data['Avg Price']:.2f}")
        
        with st.form("exit_trade_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                exit_qty = st.number_input(
                    f"Exit Quantity (Max: {trade_data['Qty']}) *", 
                    min_value=1, 
                    max_value=int(trade_data['Qty']),
                    value=int(trade_data['Qty'])
                )
                exit_price = st.number_input("Exit Price per Unit (₹) *", min_value=0.01, value=100.00, step=0.01, format="%.2f")
            
            with col2:
                exit_fees = st.number_input("Exit Fees (₹)", min_value=0.00, value=0.00, step=0.01, format="%.2f")
            
            submitted = st.form_submit_button("Calculate P&L")
            
            if submitted:
                # Calculate profit/loss
                entry_price = trade_data['Avg Price']
                gross_pnl = round((exit_price - entry_price) * exit_qty, 2)
                net_pnl = round(gross_pnl - exit_fees, 2)
                
                st.success("**P&L Calculation:**")
                st.write(f"Gross P&L: ₹{gross_pnl:.2f}")
                st.write(f"Net P&L (after fees): ₹{net_pnl:.2f}")
                
                # Show quick notification for P&L calculation
                if net_pnl > 0:
                    st.toast(f"💰 Profit Preview: +₹{net_pnl:.2f} ready to distribute!", icon="💰")
                elif net_pnl < 0:
                    st.toast(f"📊 Loss Preview: ₹{net_pnl:.2f} calculated for exit", icon="📊")
                else:
                    st.toast("📊 Breakeven calculated - no profit or loss", icon="📊")
                
                # Get linked accounts and calculate profit distribution
                linked_accounts = trade_data['Accounts'].split(',')
                capital_shares = calculate_capital_share(st.session_state.accounts, linked_accounts)
                
                st.success("**Profit Distribution:**")
                for account, share in capital_shares.items():
                    account_profit = round(net_pnl * share, 2)
                    account_name = st.session_state.accounts[st.session_state.accounts['User ID']==account]['Name'].iloc[0]
                    st.write(f"{account_name}: ₹{account_profit:.2f} ({share*100:.2f}%)")
                
                # Store exit details in session state for confirmation
                st.session_state.exit_trade_details = {
                    'trade_id': trade_id,
                    'trade_data': trade_data,
                    'exit_qty': exit_qty,
                    'exit_price': exit_price,
                    'exit_fees': exit_fees,
                    'net_pnl': net_pnl,
                    'capital_shares': capital_shares,
                    'entry_price': entry_price
                }
        
        # Confirmation section outside the form
        if 'exit_trade_details' in st.session_state and st.session_state.exit_trade_details['trade_id'] == trade_id:
            st.markdown("---")
            st.warning("⚠️ Please confirm the trade exit details above before proceeding.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm Exit Trade", type="primary", use_container_width=True):
                    execute_trade_exit()
            
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    if 'exit_trade_details' in st.session_state:
                        del st.session_state.exit_trade_details
                    st.rerun()

def execute_trade_exit():
    """Execute the trade exit with the stored details"""
    if 'exit_trade_details' not in st.session_state:
        st.error("No exit details found. Please recalculate.")
        return
    
    details = st.session_state.exit_trade_details
    
    try:
        # Distribute profit to accounts
        for account, share in details['capital_shares'].items():
            account_profit = details['net_pnl'] * share
            update_account_profit(account, account_profit)
            st.session_state.accounts.loc[
                st.session_state.accounts['User ID'] == account, 'Profit (₹)'
            ] += account_profit
        
        # Record trade history
        history_data = {
            'Trade ID': details['trade_id'],
            'Symbol': details['trade_data']['Symbol'],
            'Entry Qty': details['exit_qty'],
            'Entry Price': details['entry_price'],
            'Exit Qty': details['exit_qty'],
            'Exit Price': details['exit_price'],
            'Profit/Loss': details['net_pnl'],
            'Date': date.today(),
            'Accounts': details['trade_data']['Accounts']
        }
        
        save_trade_history_to_db(history_data)
        
        trade_history_entry = pd.DataFrame([history_data])
        st.session_state.trade_history = pd.concat([st.session_state.trade_history, trade_history_entry], ignore_index=True)
        
        # Update or close trade
        if details['exit_qty'] == details['trade_data']['Qty']:
            # Full exit - mark as closed
            update_trade_in_db(details['trade_id'], Status='Closed')
            st.session_state.trades.loc[
                st.session_state.trades['Trade ID'] == details['trade_id'], 'Status'
            ] = 'Closed'
        else:
            # Partial exit - update quantity
            remaining_qty = details['trade_data']['Qty'] - details['exit_qty']
            update_trade_in_db(details['trade_id'], Qty=remaining_qty)
            st.session_state.trades.loc[
                st.session_state.trades['Trade ID'] == details['trade_id'], 'Qty'
            ] = remaining_qty
        
        # Clear the stored details
        del st.session_state.exit_trade_details
        
        # Show appropriate celebration based on profit/loss
        if details['net_pnl'] > 0:
            st.success(f"✅ Trade exited successfully! Net P&L: ₹{details['net_pnl']:.2f}")
            st.toast(f"🎉 Profitable Trade: +₹{details['net_pnl']:.2f} from {details['trade_data']['Symbol']}", icon="🎉")
            st.balloons()
        elif details['net_pnl'] < 0:
            st.success(f"✅ Trade exited successfully! Net P&L: ₹{details['net_pnl']:.2f}")
            st.toast(f"📉 Trade Closed: ₹{details['net_pnl']:.2f} from {details['trade_data']['Symbol']}", icon="📉")
        else:
            st.success(f"✅ Trade exited successfully! Net P&L: ₹{details['net_pnl']:.2f}")
            st.toast(f"📊 Breakeven Trade: {details['trade_data']['Symbol']} closed at ₹0.00", icon="📊")
        st.rerun()
        
    except Exception as e:
        st.error(f"Error executing trade exit: {str(e)}")
        st.error("Please try again or contact support.")

def delete_trade_form():
    st.subheader("🗑️ Delete Trade")
    
    # Get all trades (both active and closed)
    all_trades = st.session_state.trades.copy()
    
    if all_trades.empty:
        st.warning("No trades found.")
        return
    
    # Trade selection
    trade_id = st.selectbox(
        "Select Trade to Delete:",
        all_trades['Trade ID'].tolist(),
        format_func=lambda x: f"{x} - {all_trades[all_trades['Trade ID']==x]['Symbol'].iloc[0]} ({all_trades[all_trades['Trade ID']==x]['Status'].iloc[0]})"
    )
    
    if trade_id:
        trade_data = all_trades[all_trades['Trade ID'] == trade_id].iloc[0]
        
        # Display trade information
        st.info(f"**Trade Details:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Symbol:** {trade_data['Symbol']}")
            st.write(f"**Quantity:** {trade_data['Qty']}")
            st.write(f"**Avg Price:** ₹{trade_data['Avg Price']:.2f}")
            st.write(f"**Strategy:** {trade_data['Strategy']}")
        
        with col2:
            st.write(f"**Status:** {trade_data['Status']}")
            st.write(f"**Date:** {trade_data['Date']}")
            st.write(f"**Total Fees:** ₹{trade_data['Total Fees']:.2f}")
            st.write(f"**Accounts:** {trade_data['Accounts']}")
        
        st.markdown("---")
        
        # Warning message
        st.error("⚠️ **WARNING: This action cannot be undone!**")
        st.warning("Deleting a trade will:")
        st.write("• Remove the trade from the database permanently")
        st.write("• Remove all associated trade history entries")
        st.write("• **NOT** reverse any profit/loss already distributed to accounts")
        
        if trade_data['Status'] == 'Active':
            st.warning("• This is an **ACTIVE** trade - consider exiting it properly instead of deleting")
        
        # Confirmation
        st.markdown("---")
        confirm_text = st.text_input(
            f"Type 'DELETE {trade_id}' to confirm deletion:",
            placeholder=f"DELETE {trade_id}"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Delete Trade", type="primary", use_container_width=True):
                if confirm_text == f"DELETE {trade_id}":
                    try:
                        # Delete from database
                        delete_trade_from_db(trade_id)
                        delete_trade_history_from_db(trade_id)
                        
                        # Remove from session state
                        st.session_state.trades = st.session_state.trades[
                            st.session_state.trades['Trade ID'] != trade_id
                        ]
                        
                        # Also remove from trade history session state
                        st.session_state.trade_history = st.session_state.trade_history[
                            st.session_state.trade_history['Trade ID'] != trade_id
                        ]
                        
                        st.success(f"✅ Trade {trade_id} deleted successfully!")
                        st.toast(f"🗑️ Trade Deleted: {trade_data['Symbol']} ({trade_id})", icon="🗑️")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error deleting trade: {str(e)}")
                        st.error("Please try again or contact support.")
                else:
                    st.error("❌ Confirmation text doesn't match. Please type exactly as shown.")
        
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.rerun()

def analytics_dashboard():
    st.header("📊 Analytics Dashboard")
    
    if st.session_state.accounts.empty:
        st.warning("No data available for analytics.")
        return
    
    # Performance metrics
    accounts_df = st.session_state.accounts.copy()
    total_capital = accounts_df['Capital (₹)'].sum()
    total_profit = accounts_df['Profit (₹)'].sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        roi = (total_profit / total_capital * 100) if total_capital > 0 else 0
        st.metric("Overall ROI", f"{roi:.2f}%")
    
    with col2:
        profitable_accounts = len(accounts_df[accounts_df['Profit (₹)'] > 0])
        st.metric("Profitable Accounts", f"{profitable_accounts}/{len(accounts_df)}")
    
    with col3:
        if not st.session_state.trade_history.empty:
            avg_pnl = st.session_state.trade_history['Profit/Loss'].mean()
            st.metric("Avg P&L per Trade", f"₹{avg_pnl:.2f}")
        else:
            st.metric("Avg P&L per Trade", "₹0.00")
    
    # Charts
    st.markdown("---")
    
    if not st.session_state.trade_history.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # P&L over time
            fig_pnl = px.line(
                st.session_state.trade_history.sort_values('Date'),
                x='Date',
                y='Profit/Loss',
                title='P&L Over Time',
                markers=True
            )
            st.plotly_chart(fig_pnl, use_container_width=True)
        
        with col2:
            # P&L by symbol
            symbol_pnl = st.session_state.trade_history.groupby('Symbol')['Profit/Loss'].sum().reset_index()
            fig_symbol = px.bar(
                symbol_pnl,
                x='Symbol',
                y='Profit/Loss',
                title='P&L by Symbol',
                color='Profit/Loss',
                color_continuous_scale=['red', 'yellow', 'green']
            )
            st.plotly_chart(fig_symbol, use_container_width=True)
    
    # Account performance table
    st.subheader("📈 Account Performance")
    accounts_df['ROI (%)'] = (accounts_df['Profit (₹)'] / accounts_df['Capital (₹)'] * 100).round(2)
    accounts_df['ROI (%)'] = accounts_df['ROI (%)'].fillna(0)
    
    st.dataframe(accounts_df.sort_values('ROI (%)', ascending=False), use_container_width=True)

def trade_history_dashboard():
    st.header("📚 Trade History")
    
    if st.session_state.trade_history.empty:
        st.info("📝 No trade history available yet. Complete some trades to see history here.")
        return
    
    # Reload fresh data from database
    fresh_history = load_trade_history_from_db()
    st.session_state.trade_history = fresh_history
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_trades = len(st.session_state.trade_history)
        st.metric("📊 Total Trades", total_trades)
        
        # Trade count milestones
        if 'last_trade_count' not in st.session_state:
            st.session_state.last_trade_count = 0
        
        if total_trades > st.session_state.last_trade_count:
            if total_trades == 100:
                st.toast("🎯 Century Achieved: 100 Trades Completed!", icon="🎯")
                st.balloons()
            elif total_trades == 50:
                st.toast("⭐ Half Century: 50 Trades Completed!", icon="⭐")
            elif total_trades == 10:
                st.toast("🔟 Double Digits: 10 Trades Completed!", icon="🔟")
            elif total_trades == 1:
                st.toast("🎉 First Trade Completed! Welcome to trading!", icon="🎉")
        
        st.session_state.last_trade_count = total_trades
    
    with col2:
        total_pnl = st.session_state.trade_history['Profit/Loss'].sum()
        st.metric("💰 Total P&L", f"₹{total_pnl:.2f}")
    
    with col3:
        profitable_trades = len(st.session_state.trade_history[st.session_state.trade_history['Profit/Loss'] > 0])
        win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
        st.metric("🎯 Win Rate", f"{win_rate:.1f}%")
    
    with col4:
        avg_pnl = st.session_state.trade_history['Profit/Loss'].mean() if total_trades > 0 else 0
        st.metric("📈 Avg P&L", f"₹{avg_pnl:.2f}")
    
    st.markdown("---")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Symbol filter
        symbols = ['All'] + sorted(st.session_state.trade_history['Symbol'].unique().tolist())
        selected_symbol = st.selectbox("Filter by Symbol", symbols)
    
    with col2:
        # Date range filter
        if not st.session_state.trade_history.empty:
            min_date = pd.to_datetime(st.session_state.trade_history['Date']).min().date()
            max_date = pd.to_datetime(st.session_state.trade_history['Date']).max().date()
            date_range = st.date_input(
                "Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
    
    with col3:
        # P&L filter
        pnl_filter = st.selectbox(
            "P&L Filter",
            ['All', 'Profitable Only', 'Loss Only']
        )
    
    # Apply filters
    filtered_history = st.session_state.trade_history.copy()
    
    if selected_symbol != 'All':
        filtered_history = filtered_history[filtered_history['Symbol'] == selected_symbol]
    
    if pnl_filter == 'Profitable Only':
        filtered_history = filtered_history[filtered_history['Profit/Loss'] > 0]
    elif pnl_filter == 'Loss Only':
        filtered_history = filtered_history[filtered_history['Profit/Loss'] < 0]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_history['Date'] = pd.to_datetime(filtered_history['Date'])
        mask = (filtered_history['Date'].dt.date >= start_date) & (filtered_history['Date'].dt.date <= end_date)
        filtered_history = filtered_history[mask]
    
    st.markdown("---")
    
    # Display filtered results
    if filtered_history.empty:
        st.warning("No trades match the selected filters.")
    else:
        st.subheader(f"📋 Trade History ({len(filtered_history)} trades)")
        
        # Style the dataframe
        def style_pnl(val):
            if val > 0:
                return 'background-color: #d4edda; color: #155724; font-weight: bold'
            elif val < 0:
                return 'background-color: #f8d7da; color: #721c24; font-weight: bold'
            return ''
        
        # Format the display dataframe
        display_df = filtered_history.copy()
        display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
        display_df['Entry Price'] = display_df['Entry Price'].round(2)
        display_df['Exit Price'] = display_df['Exit Price'].round(2)
        display_df['Profit/Loss'] = display_df['Profit/Loss'].round(2)
        
        styled_df = display_df.style.applymap(style_pnl, subset=['Profit/Loss'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Charts for filtered data
        if len(filtered_history) > 1:
            col1, col2 = st.columns(2)
            
            with col1:
                # P&L timeline
                fig_timeline = px.line(
                    filtered_history.sort_values('Date'),
                    x='Date',
                    y='Profit/Loss',
                    title='P&L Timeline',
                    markers=True,
                    color_discrete_sequence=['#667eea']
                )
                fig_timeline.add_hline(y=0, line_dash="dash", line_color="red")
                st.plotly_chart(fig_timeline, use_container_width=True)
            
            with col2:
                # Cumulative P&L
                filtered_history_sorted = filtered_history.sort_values('Date')
                filtered_history_sorted['Cumulative P&L'] = filtered_history_sorted['Profit/Loss'].cumsum()
                
                fig_cumulative = px.line(
                    filtered_history_sorted,
                    x='Date',
                    y='Cumulative P&L',
                    title='Cumulative P&L',
                    markers=True,
                    color_discrete_sequence=['#764ba2']
                )
                fig_cumulative.add_hline(y=0, line_dash="dash", line_color="red")
                st.plotly_chart(fig_cumulative, use_container_width=True)
        
        # Export and Delete functionality
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("📥 Export Data")
        
        with col2:
            st.subheader("🗑️ Delete Options")
        
        with col3:
            st.subheader("📊 Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = filtered_history.to_csv(index=False)
            if st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name=f"trade_history_{date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            ):
                st.toast(f"📥 Data Exported: {len(filtered_history)} trades downloaded as CSV", icon="📥")
        
        with col2:
            # Delete filtered trades option
            if st.button("🗑️ Delete Filtered History", use_container_width=True, type="secondary"):
                st.session_state.show_bulk_delete = True
            
            if st.session_state.get('show_bulk_delete', False):
                st.error("⚠️ **WARNING: This will delete all filtered trade history permanently!**")
                confirm_bulk = st.text_input("Type 'DELETE ALL' to confirm:", key="bulk_delete_confirm")
                
                col_confirm1, col_confirm2 = st.columns(2)
                with col_confirm1:
                    if st.button("✅ Confirm Delete", type="primary", key="confirm_bulk_delete"):
                        if confirm_bulk == "DELETE ALL":
                            try:
                                # Delete filtered trades from database
                                for _, trade in filtered_history.iterrows():
                                    delete_trade_history_from_db(trade['Trade ID'])
                                
                                # Reload fresh data
                                st.session_state.trade_history = load_trade_history_from_db()
                                st.session_state.show_bulk_delete = False
                                
                                st.success(f"✅ Deleted {len(filtered_history)} trade history entries!")
                                st.toast(f"🗑️ Bulk Delete: {len(filtered_history)} entries removed", icon="🗑️")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error deleting trades: {str(e)}")
                        else:
                            st.error("❌ Please type 'DELETE ALL' to confirm")
                
                with col_confirm2:
                    if st.button("❌ Cancel", key="cancel_bulk_delete"):
                        st.session_state.show_bulk_delete = False
                        st.rerun()
        
        with col3:
            # Summary stats
            if st.button("Show Summary Statistics", use_container_width=True):
                st.subheader("📊 Summary Statistics")
                
                stats_col1, stats_col2 = st.columns(2)
                
                with stats_col1:
                    st.metric("Total Trades", len(filtered_history))
                    st.metric("Profitable Trades", len(filtered_history[filtered_history['Profit/Loss'] > 0]))
                    st.metric("Losing Trades", len(filtered_history[filtered_history['Profit/Loss'] < 0]))
                
                with stats_col2:
                    st.metric("Max Profit", f"₹{filtered_history['Profit/Loss'].max():.2f}")
                    st.metric("Max Loss", f"₹{filtered_history['Profit/Loss'].min():.2f}")
                    st.metric("Standard Deviation", f"₹{filtered_history['Profit/Loss'].std():.2f}")

if __name__ == "__main__":
    main()