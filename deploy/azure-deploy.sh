#!/bin/bash

# Azure Functions + Static Web Apps Deployment Script
# This script helps deploy the Birthday Countdown application to Azure

set -e

echo "🎂 Birthday Countdown - Azure Deployment Script"
echo "================================================"

# Configuration
RESOURCE_GROUP="rg-birthday-countdown"
LOCATION="eastus"
FUNCTION_APP_NAME="birthday-countdown-api"
STATIC_WEB_APP_NAME="birthday-countdown-web"
STORAGE_ACCOUNT_NAME="birthdaystorage$(date +%s)"

echo "📋 Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Function App: $FUNCTION_APP_NAME"
echo "  Static Web App: $STATIC_WEB_APP_NAME"
echo "  Storage Account: $STORAGE_ACCOUNT_NAME"
echo ""

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "🔐 Please log in to Azure:"
    az login
fi

echo "✅ Azure CLI is ready"

# Create resource group
echo "📦 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create storage account for Azure Functions
echo "💾 Creating storage account..."
az storage account create \
    --name $STORAGE_ACCOUNT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS

# Create Azure Functions app
echo "⚡ Creating Azure Functions app..."
az functionapp create \
    --resource-group $RESOURCE_GROUP \
    --consumption-plan-location $LOCATION \
    --runtime python \
    --runtime-version 3.9 \
    --functions-version 4 \
    --name $FUNCTION_APP_NAME \
    --storage-account $STORAGE_ACCOUNT_NAME \
    --os-type Linux

echo "🔧 Configuring Function App settings..."
az functionapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $FUNCTION_APP_NAME \
    --settings "FUNCTIONS_WORKER_RUNTIME=python" "AzureWebJobsFeatureFlags=EnableWorkerIndexing"

# Deploy Azure Functions
echo "🚀 Deploying Azure Functions..."
cd src/api
func azure functionapp publish $FUNCTION_APP_NAME --python
cd ../..

# Get Function App URL
FUNCTION_URL=$(az functionapp show --resource-group $RESOURCE_GROUP --name $FUNCTION_APP_NAME --query "defaultHostName" -o tsv)
echo "✅ Function App deployed: https://$FUNCTION_URL"

echo ""
echo "🌐 Next Steps for Static Web App:"
echo "1. Go to Azure Portal: https://portal.azure.com"
echo "2. Create a new Static Web App"
echo "3. Connect to your GitHub repository"
echo "4. Set build configuration:"
echo "   - App location: src/web"
echo "   - API location: (leave empty - we're using separate Functions)"
echo "   - Output location: ."
echo ""
echo "🔗 Your Function App API URL: https://$FUNCTION_URL/api/nextbirthday"
echo ""
echo "🎉 Deployment completed successfully!"