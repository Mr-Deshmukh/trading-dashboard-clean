#!/usr/bin/env python3
"""
Create clean deployment package without credentials
"""

import os
import shutil

def create_clean_deployment():
    """Create clean deployment directory"""
    
    # Create clean directory
    clean_dir = "clean-deploy"
    if os.path.exists(clean_dir):
        shutil.rmtree(clean_dir)
    os.makedirs(clean_dir)
    os.makedirs(f"{clean_dir}/.streamlit")
    
    # Copy essential files
    files_to_copy = [
        "dashboard.py",
        "requirements.txt",
        ".streamlit/config.toml"
    ]
    
    for file_path in files_to_copy:
        if os.path.exists(file_path):
            if "/" in file_path:
                # Handle subdirectory files
                dest_path = os.path.join(clean_dir, file_path)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(file_path, dest_path)
            else:
                shutil.copy2(file_path, clean_dir)
            print(f"✅ Copied {file_path}")
    
    # Create clean README
    readme_content = '''# 📈 Trading Profit Management Dashboard

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
DATABASE_URL = "postgresql://[username]:[password]@[host]:[port]/[database]?sslmode=require"
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
'''
    
    with open(f"{clean_dir}/README.md", "w") as f:
        f.write(readme_content)
    print("✅ Created README.md")
    
    # Create .gitignore
    gitignore_content = '''# Database files
*.db
*.sqlite
*.sqlite3

# Environment files
.env
.env.local
.env.production

# Local secrets (use Streamlit Cloud secrets instead)
.streamlit/secrets.toml

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log

# Temporary files
tmp/
temp/
'''
    
    with open(f"{clean_dir}/.gitignore", "w") as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore")
    
    print(f"\n🎉 Clean deployment package created in '{clean_dir}' directory!")
    print("📁 Files included:")
    for root, dirs, files in os.walk(clean_dir):
        level = root.replace(clean_dir, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")

if __name__ == "__main__":
    create_clean_deployment()