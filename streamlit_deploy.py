#!/usr/bin/env python3
"""
One-click deployment script for Streamlit Cloud
This script prepares the repository for Streamlit Cloud deployment
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def log_info(message):
    print(f"✅ {message}")

def log_warn(message):
    print(f"⚠️  {message}")

def log_error(message):
    print(f"❌ {message}")

def check_git():
    """Check if git is available and repository is initialized"""
    try:
        subprocess.run(['git', '--version'], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def create_requirements():
    """Create requirements.txt for Streamlit Cloud"""
    requirements = [
        "streamlit>=1.28.0",
        "pandas>=1.5.0",
        "numpy>=1.24.0",
        "plotly>=5.15.0",
        "yfinance>=0.2.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0"
    ]
    
    with open('requirements.txt', 'w') as f:
        f.write('\n'.join(requirements))
    
    log_info("Created requirements.txt for Streamlit Cloud")

def create_streamlit_config():
    """Create Streamlit configuration for cloud deployment"""
    config_dir = Path('.streamlit')
    config_dir.mkdir(exist_ok=True)
    
    # Create config.toml
    config_content = """[global]
developmentMode = false

[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#ff6600"
backgroundColor = "#000000"
secondaryBackgroundColor = "#1a1a1a"
textColor = "#ffffff"
"""
    
    with open(config_dir / 'config.toml', 'w') as f:
        f.write(config_content)
    
    log_info("Created Streamlit configuration")

def create_secrets_template():
    """Create secrets template for Streamlit Cloud"""
    secrets_content = """# Streamlit Cloud Secrets Template
# Copy this to your Streamlit Cloud app settings

[general]
environment = "production"

[database]
# Add your database credentials here if needed
# host = "your-db-host"
# username = "your-username" 
# password = "your-password"

[api_keys]
# Add your API keys here if needed
# alpha_vantage = "your-api-key"
# polygon = "your-api-key"
"""
    
    with open('.streamlit/secrets.toml.template', 'w') as f:
        f.write(secrets_content)
    
    log_info("Created secrets template")

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# Python
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

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite3

# Secrets (keep template)
.streamlit/secrets.toml

# Data files
data/*.csv
data/*.json
data/*.db

# SSL certificates
ssl/
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    log_info("Created .gitignore file")

def create_readme():
    """Create deployment README"""
    readme_content = """# ICT Trading System - Live Deployment

## Quick Deploy to Streamlit Cloud

1. **Fork this repository** to your GitHub account

2. **Go to [Streamlit Cloud](https://share.streamlit.io)**

3. **Connect your GitHub account**

4. **Create new app with these settings:**
   - Repository: `your-username/ict-trading-system`
   - Branch: `main`
   - Main file path: `interfaces/bloomberg_ui.py`

5. **Configure secrets** (if needed):
   - Go to app settings
   - Add secrets from `.streamlit/secrets.toml.template`

6. **Deploy!** - Your app will be live at `https://your-app-name.streamlit.app`

## Alternative Deployment Options

### Docker Deployment
```bash
# Build and run with Docker
docker build -t ict-trading-system .
docker run -p 8501:8501 ict-trading-system
```

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run interfaces/bloomberg_ui.py
```

## Environment Variables

For production deployment, set these environment variables:

- `ENVIRONMENT=production`
- `DEBUG=false`

## Support

For deployment issues, check:
1. Streamlit Cloud logs
2. GitHub repository settings
3. Requirements.txt compatibility

## Security Notes

- Never commit real API keys or passwords
- Use Streamlit Cloud secrets for sensitive data
- Enable HTTPS in production
- Consider adding authentication for public deployments
"""
    
    with open('README_DEPLOYMENT.md', 'w') as f:
        f.write(readme_content)
    
    log_info("Created deployment README")

def init_git_repo():
    """Initialize git repository if not exists"""
    if not os.path.exists('.git'):
        try:
            subprocess.run(['git', 'init'], check=True)
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit for deployment'], check=True)
            log_info("Initialized git repository")
            return True
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to initialize git repository: {e}")
            return False
    else:
        log_info("Git repository already exists")
        return True

def show_deployment_instructions():
    """Show final deployment instructions"""
    print("\n" + "="*60)
    print("🚀 DEPLOYMENT READY!")
    print("="*60)
    print("\n📋 Next Steps:")
    print("\n1. Push to GitHub:")
    print("   git remote add origin https://github.com/yourusername/ict-trading-system.git")
    print("   git push -u origin main")
    print("\n2. Deploy to Streamlit Cloud:")
    print("   • Go to https://share.streamlit.io")
    print("   • Connect GitHub account")
    print("   • Select your repository")
    print("   • Main file: interfaces/bloomberg_ui.py")
    print("   • Click Deploy!")
    print("\n3. Alternative - Docker deployment:")
    print("   ./deploy.sh")
    print("\n4. Local testing:")
    print("   streamlit run interfaces/bloomberg_ui.py")
    print("\n🔗 Your app will be live at:")
    print("   https://your-app-name.streamlit.app")
    print("\n" + "="*60)

def main():
    """Main deployment preparation function"""
    print("🚀 Preparing ICT Trading System for Live Deployment")
    print("="*60)
    
    # Check prerequisites
    if not check_git():
        log_error("Git is not installed. Please install Git first.")
        sys.exit(1)
    
    # Create deployment files
    create_requirements()
    create_streamlit_config()
    create_secrets_template()
    create_gitignore()
    create_readme()
    
    # Initialize git repository
    if init_git_repo():
        log_info("Repository prepared for deployment")
    else:
        log_warn("Git repository setup had issues, but files are ready")
    
    # Show instructions
    show_deployment_instructions()

if __name__ == "__main__":
    main()
