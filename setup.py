#!/usr/bin/env python3
"""
Setup script for Trading Profit Management Dashboard
Installs dependencies and initializes the database
"""

import subprocess
import sys
import sqlite3
import os
from pathlib import Path

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def check_package(package):
    """Check if a package is already installed"""
    try:
        __import__(package)
        return True
    except ImportError:
        return False

def install_dependencies():
    """Install all required dependencies"""
    print("🔧 Installing dependencies...")
    
    dependencies = [
        "streamlit",
        "pandas", 
        "numpy",
        "plotly"
    ]
    
    installed_count = 0
    
    for package in dependencies:
        if check_package(package):
            print(f"✅ {package} is already installed")
            installed_count += 1
        else:
            print(f"📦 Installing {package}...")
            if install_package(package):
                installed_count += 1
    
    print(f"\n📊 Installation Summary: {installed_count}/{len(dependencies)} packages ready")
    return installed_count == len(dependencies)

def initialize_database():
    """Initialize the SQLite database"""
    print("\n🗄️ Initializing database...")
    
    db_file = "trading_dashboard.db"
    
    try:
        conn = sqlite3.connect(db_file)
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
        
        print(f"✅ Database '{db_file}' initialized successfully")
        print("📊 Created tables: accounts, trades, trade_history")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

def create_requirements_file():
    """Create requirements.txt file"""
    print("\n📝 Creating requirements.txt...")
    
    requirements = [
        "streamlit>=1.28.0",
        "pandas>=1.5.0",
        "numpy>=1.24.0", 
        "plotly>=5.15.0"
    ]
    
    try:
        with open("requirements.txt", "w") as f:
            f.write("\n".join(requirements))
        print("✅ requirements.txt created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create requirements.txt: {str(e)}")
        return False

def run_tests():
    """Run basic tests to verify setup"""
    print("\n🧪 Running setup verification tests...")
    
    try:
        # Test imports
        import streamlit
        import pandas
        import numpy
        import plotly
        print("✅ All packages import successfully")
        
        # Test database connection
        conn = sqlite3.connect("trading_dashboard.db")
        cursor = conn.cursor()
        
        # Test table creation
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        expected_tables = {"accounts", "trades", "trade_history"}
        actual_tables = {table[0] for table in tables}
        
        if expected_tables.issubset(actual_tables):
            print("✅ Database tables verified")
        else:
            missing = expected_tables - actual_tables
            print(f"❌ Missing database tables: {missing}")
            return False
            
        conn.close()
        
        # Test dashboard import
        try:
            import dashboard
            print("✅ Dashboard module imports successfully")
        except Exception as e:
            print(f"❌ Dashboard import failed: {str(e)}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Setup verification failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print("🚀 Trading Dashboard Setup Script")
    print("=" * 50)
    
    success_steps = 0
    total_steps = 4
    
    # Step 1: Install dependencies
    if install_dependencies():
        success_steps += 1
    
    # Step 2: Initialize database
    if initialize_database():
        success_steps += 1
    
    # Step 3: Create requirements file
    if create_requirements_file():
        success_steps += 1
    
    # Step 4: Run verification tests
    if run_tests():
        success_steps += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Setup Summary: {success_steps}/{total_steps} steps completed")
    
    if success_steps == total_steps:
        print("🎉 Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("   Run: streamlit run dashboard.py")
        print("   Open: http://localhost:8501")
        print("\n📁 Files created:")
        print("   - trading_dashboard.db (SQLite database)")
        print("   - requirements.txt (dependency list)")
    else:
        print("⚠️  Setup completed with some issues")
        print("   Check the error messages above and retry")
    
    return success_steps == total_steps

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)