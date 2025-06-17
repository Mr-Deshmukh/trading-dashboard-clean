"""
Database adapter for Trading Dashboard
Supports both SQLite and PostgreSQL databases
"""

import sqlite3
import pandas as pd
import os
try:
    from sqlalchemy import create_engine, text
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

DATABASE_URL = os.getenv('DATABASE_URL')
DB_FILE = os.getenv('DATABASE_PATH', 'trading_dashboard.db')
USE_POSTGRESQL = DATABASE_URL is not None and POSTGRESQL_AVAILABLE

class DatabaseAdapter:
    """Unified database adapter for SQLite and PostgreSQL"""
    
    def __init__(self):
        self.use_postgresql = USE_POSTGRESQL
        if self.use_postgresql:
            self.engine = create_engine(DATABASE_URL)
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        if self.use_postgresql:
            with self.engine.connect() as conn:
                if params:
                    result = conn.execute(text(query), params)
                else:
                    result = conn.execute(text(query))
                conn.commit()
                return result
        else:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            result = cursor.fetchall()
            conn.close()
            return result
    
    def read_sql(self, query):
        """Read SQL query into pandas DataFrame"""
        try:
            if self.use_postgresql:
                return pd.read_sql_query(query, self.engine)
            else:
                conn = sqlite3.connect(DB_FILE)
                df = pd.read_sql_query(query, conn)
                conn.close()
                return df
        except Exception:
            return pd.DataFrame()
    
    def save_account(self, user_id, name, email, capital, profit=0):
        """Save account to database"""
        if self.use_postgresql:
            query = '''
                INSERT INTO accounts (user_id, name, email, capital, profit)
                VALUES (:user_id, :name, :email, :capital, :profit)
                ON CONFLICT (user_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    email = EXCLUDED.email,
                    capital = EXCLUDED.capital,
                    profit = EXCLUDED.profit
            '''
        else:
            query = '''
                INSERT OR REPLACE INTO accounts (user_id, name, email, capital, profit)
                VALUES (?, ?, ?, ?, ?)
            '''
        
        params = {'user_id': user_id, 'name': name, 'email': email, 'capital': capital, 'profit': profit} if self.use_postgresql else (user_id, name, email, capital, profit)
        self.execute_query(query, params)
    
    def update_account_capital(self, user_id, new_capital):
        """Update account capital"""
        if self.use_postgresql:
            query = 'UPDATE accounts SET capital = :capital WHERE user_id = :user_id'
            params = {'capital': new_capital, 'user_id': user_id}
        else:
            query = 'UPDATE accounts SET capital = ? WHERE user_id = ?'
            params = (new_capital, user_id)
        
        self.execute_query(query, params)
    
    def update_account_profit(self, user_id, profit_change):
        """Add profit to account"""
        if self.use_postgresql:
            query = 'UPDATE accounts SET profit = profit + :profit_change WHERE user_id = :user_id'
            params = {'profit_change': profit_change, 'user_id': user_id}
        else:
            query = 'UPDATE accounts SET profit = profit + ? WHERE user_id = ?'
            params = (profit_change, user_id)
        
        self.execute_query(query, params)
    
    def delete_account(self, user_id):
        """Delete account from database"""
        if self.use_postgresql:
            query = 'DELETE FROM accounts WHERE user_id = :user_id'
            params = {'user_id': user_id}
        else:
            query = 'DELETE FROM accounts WHERE user_id = ?'
            params = (user_id,)
        
        self.execute_query(query, params)
    
    def save_trade(self, trade_data):
        """Save trade to database"""
        if self.use_postgresql:
            query = '''
                INSERT INTO trades 
                (trade_id, symbol, qty, avg_price, strategy, total_fees, date, accounts, status, positions)
                VALUES (:trade_id, :symbol, :qty, :avg_price, :strategy, :total_fees, :date, :accounts, :status, :positions)
                ON CONFLICT (trade_id) DO UPDATE SET
                    symbol = EXCLUDED.symbol,
                    qty = EXCLUDED.qty,
                    avg_price = EXCLUDED.avg_price,
                    strategy = EXCLUDED.strategy,
                    total_fees = EXCLUDED.total_fees,
                    date = EXCLUDED.date,
                    accounts = EXCLUDED.accounts,
                    status = EXCLUDED.status,
                    positions = EXCLUDED.positions
            '''
            params = {
                'trade_id': trade_data['Trade ID'],
                'symbol': trade_data['Symbol'],
                'qty': trade_data['Qty'],
                'avg_price': trade_data['Avg Price'],
                'strategy': trade_data['Strategy'],
                'total_fees': trade_data['Total Fees'],
                'date': trade_data['Date'],
                'accounts': trade_data['Accounts'],
                'status': trade_data['Status'],
                'positions': trade_data['Positions']
            }
        else:
            query = '''
                INSERT OR REPLACE INTO trades 
                (trade_id, symbol, qty, avg_price, strategy, total_fees, date, accounts, status, positions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                trade_data['Trade ID'], trade_data['Symbol'], trade_data['Qty'],
                trade_data['Avg Price'], trade_data['Strategy'], trade_data['Total Fees'],
                trade_data['Date'], trade_data['Accounts'], trade_data['Status'], trade_data['Positions']
            )
        
        self.execute_query(query, params)
    
    def update_trade(self, trade_id, **kwargs):
        """Update trade in database"""
        if not kwargs:
            return
        
        column_map = {
            'Qty': 'qty', 'Avg Price': 'avg_price', 'Total Fees': 'total_fees',
            'Status': 'status', 'Positions': 'positions'
        }
        
        updates = []
        params = {}
        
        for key, value in kwargs.items():
            column = column_map.get(key, key.lower())
            if self.use_postgresql:
                updates.append(f"{column} = :{column}")
                params[column] = value
            else:
                updates.append(f"{column} = ?")
        
        if self.use_postgresql:
            query = f"UPDATE trades SET {', '.join(updates)} WHERE trade_id = :trade_id"
            params['trade_id'] = trade_id
        else:
            query = f"UPDATE trades SET {', '.join(updates)} WHERE trade_id = ?"
            params = tuple(kwargs.values()) + (trade_id,)
        
        self.execute_query(query, params)
    
    def save_trade_history(self, history_data):
        """Save trade history to database"""
        if self.use_postgresql:
            query = '''
                INSERT INTO trade_history 
                (trade_id, symbol, entry_qty, entry_price, exit_qty, exit_price, profit_loss, date, accounts)
                VALUES (:trade_id, :symbol, :entry_qty, :entry_price, :exit_qty, :exit_price, :profit_loss, :date, :accounts)
            '''
            params = {
                'trade_id': history_data['Trade ID'],
                'symbol': history_data['Symbol'],
                'entry_qty': history_data['Entry Qty'],
                'entry_price': history_data['Entry Price'],
                'exit_qty': history_data['Exit Qty'],
                'exit_price': history_data['Exit Price'],
                'profit_loss': history_data['Profit/Loss'],
                'date': history_data['Date'],
                'accounts': history_data['Accounts']
            }
        else:
            query = '''
                INSERT INTO trade_history 
                (trade_id, symbol, entry_qty, entry_price, exit_qty, exit_price, profit_loss, date, accounts)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                history_data['Trade ID'], history_data['Symbol'], history_data['Entry Qty'],
                history_data['Entry Price'], history_data['Exit Qty'], history_data['Exit Price'],
                history_data['Profit/Loss'], history_data['Date'], history_data['Accounts']
            )
        
        self.execute_query(query, params)

# Global database adapter instance
db = DatabaseAdapter()