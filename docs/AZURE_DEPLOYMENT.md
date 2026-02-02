# 🚀 Azure Deployment Guide: Functions + Static Web Apps

This guide walks you through deploying the Birthday Countdown application using Azure Functions for the API and Azure Static Web Apps for the frontend.

## 📋 Prerequisites

### Required Tools
- **Azure CLI**: [Install Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Azure Functions Core Tools**: [Install Functions Core Tools](https://docs.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- **Git**: For repository management
- **GitHub Account**: For Static Web Apps integration

### Installation Commands
```bash
# Install Azure CLI (macOS)
brew install azure-cli

# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4 --unsafe-perm true

# Verify installations
az --version
func --version
```

## 🎯 Deployment Architecture

```
GitHub Repository
       ↓
┌─────────────────┐    API Calls    ┌──────────────────┐
│ Azure Static    │ ──────────────► │ Azure Functions  │
│ Web Apps        │                 │ (Python API)     │
│ (Frontend)      │ ◄────────────── │                  │
└─────────────────┘    JSON         └──────────────────┘
```

## 📦 Step 1: Prepare Your Repository

### 1.1 Push Code to GitHub
```bash
# Initialize git repository (if not already done)
git init
git add .
git commit -m "Initial commit: Birthday Countdown App"

# Create GitHub repository and push
git remote add origin https://github.com/yourusername/birthday-countdown.git
git branch -M main
git push -u origin main
```

### 1.2 Verify Repository Structure
Ensure your repository has this structure:
```
birthday-countdown/
├── src/
│   ├── api/                 # Azure Functions backend
│   │   ├── function_app.py
│   │   ├── host.json
│   │   ├── local.settings.json
│   │   └── requirements.txt
│   └── web/                 # Frontend for Static Web Apps
│       ├── index.html
│       ├── app.js
│       ├── styles.css
│       └── staticwebapp.config.json
└── deploy/
    └── azure-deploy.sh
```

## ⚡ Step 2: Deploy Azure Functions (Backend API)

### 2.1 Login to Azure
```bash
az login
```

### 2.2 Set Your Subscription (if you have multiple)
```bash
# List subscriptions
az account list --output table

# Set active subscription
az account set --subscription "Your Subscription Name"
```

### 2.3 Run Automated Deployment Script
```bash
# Make script executable and run
chmod +x deploy/azure-deploy.sh
./deploy/azure-deploy.sh
```

### 2.4 Manual Deployment (Alternative)
If you prefer manual steps:

```bash
# Create resource group
az group create --name rg-birthday-countdown --location eastus

# Create storage account
az storage account create \
    --name birthdaystorage$(date +%s) \
    --resource-group rg-birthday-countdown \
    --location eastus \
    --sku Standard_LRS

# Create Function App
az functionapp create \
    --resource-group rg-birthday-countdown \
    --consumption-plan-location eastus \
    --runtime python \
    --runtime-version 3.9 \
    --functions-version 4 \
    --name birthday-countdown-api \
    --storage-account birthdaystorage$(date +%s) \
    --os-type Linux

# Deploy functions
cd src/api
func azure functionapp publish birthday-countdown-api --python
cd ../..
```

### 2.5 Test Your Function App
```bash
# Get your Function App URL
FUNCTION_URL=$(az functionapp show --resource-group rg-birthday-countdown --name birthday-countdown-api --query "defaultHostName" -o tsv)

# Test the API
curl "https://$FUNCTION_URL/api/nextbirthday?dob=1990-05-15"
```

## 🌐 Step 3: Deploy Azure Static Web Apps (Frontend)

### 3.1 Create Static Web App via Azure Portal

1. **Go to Azure Portal**: https://portal.azure.com
2. **Create Resource** → Search for "Static Web Apps"
3. **Click "Create"**

### 3.2 Configure Static Web App

**Basic Settings:**
- **Subscription**: Your Azure subscription
- **Resource Group**: `rg-birthday-countdown` (same as Functions)
- **Name**: `birthday-countdown-web`
- **Plan Type**: Free (for development/testing)
- **Region**: East US 2 (or closest to your users)

**Deployment Details:**
- **Source**: GitHub
- **GitHub Account**: Authorize your GitHub account
- **Organization**: Your GitHub username
- **Repository**: `birthday-countdown` (your repo name)
- **Branch**: `main`

**Build Details:**
- **Build Presets**: Custom
- **App location**: `src/web`
- **Api location**: *(leave empty)*
- **Output location**: `.`

### 3.3 Complete Deployment
1. Click **"Review + Create"**
2. Click **"Create"**
3. Wait for deployment to complete (2-3 minutes)

### 3.4 GitHub Actions Workflow
Azure automatically creates a GitHub Actions workflow file at:
`.github/workflows/azure-static-web-apps-<random-name>.yml`

This workflow will:
- Build and deploy your frontend automatically
- Trigger on every push to main branch
- Deploy to your Static Web App

## 🔗 Step 4: Connect Frontend to Backend

### 4.1 Configure CORS (if needed)
```bash
# Allow Static Web App to call Function App
az functionapp cors add \
    --resource-group rg-birthday-countdown \
    --name birthday-countdown-api \
    --allowed-origins https://your-static-web-app-url.azurestaticapps.net
```

### 4.2 Update API URL (if using separate Functions)
If you're not using integrated API, update `src/web/app.js`:

```javascript
const CONFIG = {
    API_BASE_URL: 'https://birthday-countdown-api.azurewebsites.net/api/nextbirthday'
};
```

## 🧪 Step 5: Test Your Deployment

### 5.1 Get Your URLs
```bash
# Function App URL
az functionapp show --resource-group rg-birthday-countdown --name birthday-countdown-api --query "defaultHostName" -o tsv

# Static Web App URL
az staticwebapp show --resource-group rg-birthday-countdown --name birthday-countdown-web --query "defaultHostname" -o tsv
```

### 5.2 Test the Complete Application
1. **Open your Static Web App URL** in a browser
2. **Enter a date of birth** in the form
3. **Click "Calculate Next Birthday"**
4. **Verify the results** are displayed correctly

### 5.3 Test API Directly
```bash
curl "https://birthday-countdown-api.azurewebsites.net/api/nextbirthday?dob=1990-05-15"
```

## 🔧 Step 6: Configure Custom Domain (Optional)

### 6.1 Add Custom Domain to Static Web App
1. Go to your Static Web App in Azure Portal
2. Click **"Custom domains"**
3. Click **"Add"** → **"Custom domain on Azure DNS"** or **"Custom domain on other DNS"**
4. Follow the verification steps

### 6.2 SSL Certificate
Azure Static Web Apps automatically provides SSL certificates for custom domains.

## 📊 Step 7: Monitor and Manage

### 7.1 View Logs
```bash
# Function App logs
az webapp log tail --resource-group rg-birthday-countdown --name birthday-countdown-api

# Static Web App deployment logs (check GitHub Actions)
```

### 7.2 Application Insights (Optional)
Enable Application Insights for monitoring:
```bash
az monitor app-insights component create \
    --app birthday-countdown-insights \
    --location eastus \
    --resource-group rg-birthday-countdown
```

## 🚀 Step 8: Continuous Deployment

### 8.1 Automatic Deployments
- **Frontend**: Automatically deploys via GitHub Actions on every push
- **Backend**: Set up GitHub Actions for Functions deployment

### 8.2 Create Functions Deployment Workflow
Create `.github/workflows/azure-functions.yml`:

```yaml
name: Deploy Azure Functions

on:
  push:
    branches: [ main ]
    paths: [ 'src/api/**' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd src/api
        pip install -r requirements.txt
    
    - name: Deploy to Azure Functions
      uses: Azure/functions-action@v1
      with:
        app-name: birthday-countdown-api
        package: src/api
        publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}
```

## 🎉 Deployment Complete!

Your Birthday Countdown application is now live on Azure with:

- ⚡ **Serverless Backend**: Azure Functions with auto-scaling
- 🌐 **Global Frontend**: Azure Static Web Apps with CDN
- 🔒 **HTTPS**: Automatic SSL certificates
- 🚀 **CI/CD**: Automatic deployments via GitHub Actions
- 💰 **Cost-Effective**: Pay-per-execution pricing

### Your Live URLs:
- **Frontend**: `https://your-static-web-app.azurestaticapps.net`
- **API**: `https://birthday-countdown-api.azurewebsites.net/api/nextbirthday`

## 🛠️ Troubleshooting

### Common Issues:

1. **CORS Errors**:
   ```bash
   az functionapp cors add --resource-group rg-birthday-countdown --name birthday-countdown-api --allowed-origins "*"
   ```

2. **Function App Not Starting**:
   - Check Python version (must be 3.9)
   - Verify requirements.txt is correct
   - Check Application Insights logs

3. **Static Web App Build Fails**:
   - Verify app location is `src/web`
   - Check staticwebapp.config.json syntax
   - Review GitHub Actions logs

4. **API Not Found**:
   - Verify Function App is running
   - Check function name and route
   - Test API URL directly

### Get Help:
- **Azure Functions**: [Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/)
- **Static Web Apps**: [Documentation](https://docs.microsoft.com/en-us/azure/static-web-apps/)
- **GitHub Actions**: [Documentation](https://docs.github.com/en/actions)

---

**🎂 Happy Birthday Counting in the Cloud! 🎉**