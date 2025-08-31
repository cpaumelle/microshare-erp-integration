# Microshare Platform Credentials Guide

Get Microshare API access for your ERP integration development.

## Fast Track: Use Generic Credentials (Recommended)

**For development and testing**, use the working credentials in `.env.example`:

```bash
cp .env.example .env
# Ready to use immediately!
```

## Get Your Own Development Account

### Step 1: Create Account
1. Go to https://dapp.microshare.io
2. Click "Sign Up" on homepage
3. **Need a free voucher?** Contact your Microshare success manager

### Step 2: Generate API Key (Desktop Browser Required)
1. Login to https://dapp.microshare.io
2. Top right hamburger menu (☰) → "Exit to Console"
3. Look for "Manage" link on top left → click to show left navigation
4. Scroll to bottom of left nav → click "Keys"
5. "App Keys" → CREATE NEW APP
6. Name it "ERP Integration Development"
7. **Copy API key immediately** and store securely

### Step 3: Update Environment
```bash
# Edit .env file with your credentials
MICROSHARE_USERNAME=your_username
MICROSHARE_PASSWORD=your_password  
MICROSHARE_API_KEY=your_api_key
```

## Production Environment

```bash
# Production credentials
MICROSHARE_AUTH_URL=https://auth.microshare.io
MICROSHARE_API_URL=https://api.microshare.io
MICROSHARE_USERNAME=your_prod_username
MICROSHARE_PASSWORD=your_prod_password
MICROSHARE_API_KEY=your_prod_api_key
```

**Production Setup:**
1. Create account at https://app.microshare.io
2. Follow same API key process
3. Contact support@microshare.io for production assistance

## Troubleshooting

**401 Unauthorized:**
- Verify username/password spelling
- Check API key is correct
- Try URL encoding special characters in password

**Connection Issues:**
- Check network access to *.microshare.io domains
- Verify firewall allows HTTPS connections
- Use desktop browser (mobile may not show all interface elements)

**Need Help?**
Email: support@microshare.io (mention "ERP integration development")
