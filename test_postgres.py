#!/usr/bin/env python3
"""
Test PostgreSQL connection for Aiven deployment
"""

import os
import sys

def test_postgresql_connection():
    """Test connection to Aiven PostgreSQL"""
    
    print("🧪 Testing Aiven PostgreSQL Connection")
    print("=" * 50)
    
    # Check for DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("Please set it with your Aiven connection string:")
        print("export DATABASE_URL='postgresql://user:password@host:port/database'")
        return False
    
    print(f"✅ DATABASE_URL found: {database_url[:50]}...")
    
    # Test psycopg2 import
    try:
        import psycopg2
        from sqlalchemy import create_engine, text
        print("✅ PostgreSQL dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Install with: pip install psycopg2-binary sqlalchemy")
        return False
    
    # Test connection
    try:
        print("🔌 Testing database connection...")
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected successfully!")
            print(f"📊 PostgreSQL Version: {version[:50]}...")
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("Please check:")
        print("- Database URL format")
        print("- Network connectivity")
        print("- Database credentials")
        return False
    
    # Test table creation
    try:
        print("🏗️ Testing table creation...")
        
        with engine.connect() as conn:
            # Test creating a simple table
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS test_table (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            '''))
            
            # Insert test data
            conn.execute(text('''
                INSERT INTO test_table (name) VALUES ('test') 
                ON CONFLICT DO NOTHING
            '''))
            
            # Read test data
            result = conn.execute(text("SELECT COUNT(*) FROM test_table"))
            count = result.fetchone()[0]
            
            # Clean up
            conn.execute(text("DROP TABLE test_table"))
            conn.commit()
            
            print(f"✅ Table operations successful (found {count} test records)")
        
    except Exception as e:
        print(f"❌ Table creation failed: {str(e)}")
        return False
    
    print("\n🎉 All tests passed! Your Aiven PostgreSQL is ready!")
    print("📝 Next steps:")
    print("1. Run migration: python migrate_db.py")
    print("2. Test dashboard: streamlit run dashboard.py")
    print("3. Deploy to Streamlit Cloud with DATABASE_URL secret")
    
    return True

def main():
    """Main test function"""
    success = test_postgresql_connection()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()