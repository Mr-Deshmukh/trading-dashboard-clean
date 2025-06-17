#!/usr/bin/env python3
"""
Database Migration Script for Trading Dashboard
Migrates from SQLite to PostgreSQL/MySQL for production deployment
"""

import sqlite3
import pandas as pd
import os
import sys
from sqlalchemy import create_engine

def migrate_sqlite_to_sql(sqlite_path, target_url, target_type='postgresql'):
    """
    Migrate SQLite database to PostgreSQL or MySQL
    
    Args:
        sqlite_path: Path to SQLite database file
        target_url: Connection URL for target database
        target_type: 'postgresql' or 'mysql'
    """
    
    print(f"🔄 Starting migration from SQLite to {target_type.upper()}...")
    
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(sqlite_path)
        print(f"✅ Connected to SQLite: {sqlite_path}")
        
        # Read all tables
        accounts = pd.read_sql_query("SELECT * FROM accounts", sqlite_conn)
        trades = pd.read_sql_query("SELECT * FROM trades", sqlite_conn)
        trade_history = pd.read_sql_query("SELECT * FROM trade_history", sqlite_conn)
        
        print(f"📊 Read {len(accounts)} accounts, {len(trades)} trades, {len(trade_history)} history records")
        
        sqlite_conn.close()
        
        # Connect to target database
        engine = create_engine(target_url)
        print(f"✅ Connected to {target_type.upper()} database")
        
        # Create tables and insert data
        accounts.to_sql('accounts', engine, if_exists='replace', index=False)
        trades.to_sql('trades', engine, if_exists='replace', index=False)
        trade_history.to_sql('trade_history', engine, if_exists='replace', index=False)
        
        print("✅ Migration completed successfully!")
        print(f"📊 Migrated {len(accounts)} accounts, {len(trades)} trades, {len(trade_history)} history records")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False

def create_postgresql_schema(connection_url):
    """Create PostgreSQL tables with proper schema"""
    
    engine = create_engine(connection_url)
    
    schema_sql = """
    -- Accounts table
    CREATE TABLE IF NOT EXISTS accounts (
        user_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        capital DECIMAL(15,2) NOT NULL DEFAULT 0,
        profit DECIMAL(15,2) NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Trades table  
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
    );
    
    -- Trade history table
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
    );
    """
    
    try:
        with engine.connect() as conn:
            for statement in schema_sql.split(';'):
                if statement.strip():
                    conn.execute(statement)
            conn.commit()
        print("✅ PostgreSQL schema created successfully")
        return True
    except Exception as e:
        print(f"❌ Schema creation failed: {str(e)}")
        return False

def main():
    """Main migration script"""
    
    print("📈 Trading Dashboard Database Migration Tool")
    print("=" * 50)
    
    # Check for SQLite database
    sqlite_path = 'trading_dashboard.db'
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite database not found: {sqlite_path}")
        print("Run the dashboard locally first to create the database.")
        sys.exit(1)
    
    # Get target database URL from environment or user input
    target_url = os.getenv('DATABASE_URL')
    
    if not target_url:
        print("🔗 Enter your target database URL:")
        print("Examples:")
        print("  PostgreSQL: postgresql://user:password@host:port/database")
        print("  MySQL: mysql://user:password@host:port/database")
        target_url = input("Database URL: ").strip()
    
    if not target_url:
        print("❌ No database URL provided")
        sys.exit(1)
    
    # Determine database type
    if target_url.startswith('postgresql://'):
        db_type = 'postgresql'
        print("🐘 Detected PostgreSQL database")
        
        # Create schema first
        create_postgresql_schema(target_url)
        
    elif target_url.startswith('mysql://'):
        db_type = 'mysql'
        print("🐬 Detected MySQL database")
    else:
        print("⚠️  Unknown database type, attempting migration...")
        db_type = 'unknown'
    
    # Perform migration
    success = migrate_sqlite_to_sql(sqlite_path, target_url, db_type)
    
    if success:
        print("\n🎉 Migration completed successfully!")
        print("📝 Next steps:")
        print("1. Update your Streamlit Cloud secrets with DATABASE_URL")
        print("2. Update dashboard.py to use the new database")
        print("3. Test the connection before deploying")
    else:
        print("\n❌ Migration failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()