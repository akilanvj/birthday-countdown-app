# Azure Functions + Static Web Apps Deployment Script (PowerShell)
# This script helps deploy the Birthday Countdown application to Azure

param(
    [string]$ResourceGroup = "rg-birthday-countdown",
    [string]$Location = "eastus",
    [string]$FunctionAppName = "birthday-countdown-api",
    [string]$StaticWebAppName = "birthday-countdown-web"
)

Write-Host "🎂 Birthday Countdown - Azure Deployment Script (PowerShell)" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan

# Configuration
$StorageAccountName = "birthdaystorage$(Get-Date -Format 'yyyyMMddHHmmss')"

Write-Host "📋 Configuration:" -ForegroundColor Yellow
Write-Host "  Resource Group: $ResourceGroup"
Write-Host "  Location: $Location"
Write-Host "  Function App: $FunctionAppName"
Write-Host "  Static Web App: $StaticWebAppName"
Write-Host "  Storage Account: $StorageAccountName"
Write-Host ""

# Check if Azure CLI is installed
try {
    az --version | Out-Null
    Write-Host "✅ Azure CLI is ready" -ForegroundColor Green
} catch {
    Write-Host "❌ Azure CLI is not installed. Please install it first:" -ForegroundColor Red
    Write-Host "   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
}

# Check if logged in to Azure
try {
    az account show | Out-Null
} catch {
    Write-Host "🔐 Please log in to Azure:" -ForegroundColor Yellow
    az login
}

# Create resource group
Write-Host "📦 Creating resource group..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location

# Create storage account for Azure Functions
Write-Host "💾 Creating storage account..." -ForegroundColor Yellow
az storage account create `
    --name $StorageAccountName `
    --resource-group $ResourceGroup `
    --location $Location `
    --sku Standard_LRS

# Create Azure Functions app
Write-Host "⚡ Creating Azure Functions app..." -ForegroundColor Yellow
az functionapp create `
    --resource-group $ResourceGroup `
    --consumption-plan-location $Location `
    --runtime python `
    --runtime-version 3.9 `
    --functions-version 4 `
    --name $FunctionAppName `
    --storage-account $StorageAccountName `
    --os-type Linux

Write-Host "🔧 Configuring Function App settings..." -ForegroundColor Yellow
az functionapp config appsettings set `
    --resource-group $ResourceGroup `
    --name $FunctionAppName `
    --settings "FUNCTIONS_WORKER_RUNTIME=python" "AzureWebJobsFeatureFlags=EnableWorkerIndexing"

# Deploy Azure Functions
Write-Host "🚀 Deploying Azure Functions..." -ForegroundColor Yellow
Set-Location src/api
func azure functionapp publish $FunctionAppName --python
Set-Location ../..

# Get Function App URL
$FunctionUrl = az functionapp show --resource-group $ResourceGroup --name $FunctionAppName --query "defaultHostName" -o tsv
Write-Host "✅ Function App deployed: https://$FunctionUrl" -ForegroundColor Green

Write-Host ""
Write-Host "🌐 Next Steps for Static Web App:" -ForegroundColor Cyan
Write-Host "1. Go to Azure Portal: https://portal.azure.com"
Write-Host "2. Create a new Static Web App"
Write-Host "3. Connect to your GitHub repository"
Write-Host "4. Set build configuration:"
Write-Host "   - App location: src/web"
Write-Host "   - API location: (leave empty - we're using separate Functions)"
Write-Host "   - Output location: ."
Write-Host ""
Write-Host "🔗 Your Function App API URL: https://$FunctionUrl/api/nextbirthday" -ForegroundColor Green
Write-Host ""
Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green