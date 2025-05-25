# Live Deployment Guide

This guide covers deploying the ICT Trading System from local development to live production environments.

## Deployment Options

### 1. Cloud Platforms (Recommended)
- **Streamlit Cloud** - Free, easy deployment
- **Heroku** - Simple PaaS deployment
- **AWS EC2** - Full control, scalable
- **Google Cloud Platform** - Enterprise-grade
- **DigitalOcean** - Developer-friendly

### 2. VPS/Dedicated Server
- **Linux VPS** - Cost-effective
- **Dedicated Server** - Maximum performance
- **Docker Container** - Portable deployment

### 3. Local Network
- **Home Server** - Private deployment
- **Office Network** - Team access
- **Raspberry Pi** - Low-cost solution

## Quick Deployment: Streamlit Cloud (Free)

### Step 1: Prepare Repository
```bash
# Create requirements.txt for production
pip freeze > requirements.txt

# Create .streamlit/config.toml
mkdir -p .streamlit
```

### Step 2: GitHub Setup
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial deployment"

# Push to GitHub
git remote add origin https://github.com/yourusername/ict-trading-system.git
git push -u origin main
```

### Step 3: Deploy to Streamlit Cloud
1. Go to https://share.streamlit.io
2. Connect your GitHub account
3. Select repository: `ict-trading-system`
4. Main file path: `interfaces/bloomberg_ui.py`
5. Click "Deploy"

## Production Configuration

### Environment Variables
Create `.env` file for production:
```bash
# Production Environment
ENVIRONMENT=production
DEBUG=false

# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# API Keys (if needed)
ALPHA_VANTAGE_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here

# Security
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Streamlit Config
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Production Requirements
Create `requirements-prod.txt`:
```
streamlit>=1.28.0
pandas>=1.5.0
numpy>=1.24.0
plotly>=5.15.0
yfinance>=0.2.0
python-dotenv>=1.0.0
psycopg2-binary>=2.9.0
gunicorn>=21.0.0
```

## Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run application
CMD ["streamlit", "run", "interfaces/bloomberg_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  trading-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: trading_db
      POSTGRES_USER: trading_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## AWS EC2 Deployment

### Step 1: Launch EC2 Instance
```bash
# Choose Ubuntu 22.04 LTS
# Instance type: t3.medium (recommended)
# Security group: Allow HTTP (80), HTTPS (443), SSH (22)
```

### Step 2: Server Setup
```bash
# Connect to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip nginx -y

# Clone repository
git clone https://github.com/yourusername/ict-trading-system.git
cd ict-trading-system

# Install requirements
pip3 install -r requirements-prod.txt
```

### Step 3: Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Step 4: SSL Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### Step 5: Systemd Service
Create `/etc/systemd/system/trading-app.service`:
```ini
[Unit]
Description=ICT Trading System
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ict-trading-system
Environment=PATH=/home/ubuntu/.local/bin
ExecStart=/usr/bin/python3 -m streamlit run interfaces/bloomberg_ui.py --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable trading-app
sudo systemctl start trading-app
```

## Security Considerations

### 1. Authentication
Add user authentication to the Streamlit app:
```python
import streamlit_authenticator as stauth

# In your main app
authenticator = stauth.Authenticate(
    credentials,
    'trading_app',
    'auth_key',
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    # Show trading interface
    main_app()
elif authentication_status == False:
    st.error('Username/password is incorrect')
```

### 2. HTTPS Only
```python
# Force HTTPS in production
if st.secrets.get("ENVIRONMENT") == "production":
    if not st.session_state.get("https_redirect"):
        st.markdown("""
        <script>
        if (location.protocol !== 'https:') {
            location.replace('https:' + window.location.href.substring(window.location.protocol.length));
        }
        </script>
        """, unsafe_allow_html=True)
        st.session_state.https_redirect = True
```

### 3. Environment Secrets
Use Streamlit secrets management:
```toml
# .streamlit/secrets.toml
[database]
host = "your-db-host"
username = "your-username"
password = "your-password"

[api_keys]
alpha_vantage = "your-api-key"
```

## Monitoring and Maintenance

### 1. Health Checks
```python
# Add to your app
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### 2. Logging
```python
import logging

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/trading-app.log'),
        logging.StreamHandler()
    ]
)
```

### 3. Backup Strategy
```bash
# Database backup script
#!/bin/bash
pg_dump trading_db > backup_$(date +%Y%m%d_%H%M%S).sql
aws s3 cp backup_*.sql s3://your-backup-bucket/
```

## Performance Optimization

### 1. Caching
```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_market_data(symbol):
    return fetch_data(symbol)
```

### 2. Database Connection Pooling
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### 3. CDN for Static Assets
Use CloudFlare or AWS CloudFront for static assets.

## Scaling Considerations

### Horizontal Scaling
- Load balancer (nginx/HAProxy)
- Multiple app instances
- Shared database
- Redis for session storage

### Vertical Scaling
- Increase server resources
- Optimize database queries
- Use faster storage (SSD)

## Cost Estimation

### Free Tier Options
- **Streamlit Cloud**: Free (public repos)
- **Heroku**: $7/month (hobby tier)
- **Railway**: $5/month

### Production Options
- **AWS EC2 t3.medium**: ~$30/month
- **DigitalOcean Droplet**: ~$20/month
- **Google Cloud Run**: Pay per use

## Next Steps

1. Choose deployment platform
2. Set up domain name
3. Configure SSL certificate
4. Implement authentication
5. Set up monitoring
6. Create backup strategy
7. Test thoroughly
8. Go live!

The system is ready for production deployment with proper security, monitoring, and scaling capabilities.
