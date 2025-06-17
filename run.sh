#!/bin/bash

# Trading Dashboard Launcher Script
echo "🚀 Starting Trading Profit Management Dashboard..."
echo "📊 Loading database and initializing..."

# Check if database exists
if [ ! -f "trading_dashboard.db" ]; then
    echo "⚠️  Database not found. Running setup..."
    python setup.py
fi

# Start the dashboard
echo "🌐 Starting Streamlit server..."
echo "📱 Open http://localhost:8501 in your browser"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

streamlit run dashboard.py