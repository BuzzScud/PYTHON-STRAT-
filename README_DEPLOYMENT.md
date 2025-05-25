# ICT Trading System - Live Deployment

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
