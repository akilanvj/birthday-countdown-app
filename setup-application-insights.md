# Application Insights Setup for Birthday Countdown App

## Quick Setup Steps

### 1. Create Application Insights Resource

```bash
# Create Application Insights
az monitor app-insights component create \
    --app birthday-countdown-insights \
    --location eastus \
    --resource-group rg-birthday-countdown \
    --application-type web

# Get the instrumentation key
az monitor app-insights component show \
    --app birthday-countdown-insights \
    --resource-group rg-birthday-countdown \
    --query instrumentationKey -o tsv
```

### 2. Configure Azure Functions

Add to your Function App settings:
```bash
# Set Application Insights connection
az functionapp config appsettings set \
    --name your-function-app-name \
    --resource-group rg-birthday-countdown \
    --settings "APPINSIGHTS_INSTRUMENTATIONKEY=your-instrumentation-key"
```

### 3. View Logs in Azure Portal

1. Go to Azure Portal → Application Insights → birthday-countdown-insights
2. Click **"Logs"** in the left menu
3. Use these queries to see your app logs:

#### View All Function Logs
```kusto
traces
| where timestamp > ago(1h)
| where message contains "Birthday countdown"
| order by timestamp desc
```

#### View API Errors
```kusto
exceptions
| where timestamp > ago(1h)
| where operation_Name contains "nextbirthday"
| order by timestamp desc
```

#### View Request Details
```kusto
requests
| where timestamp > ago(1h)
| where name contains "nextbirthday"
| project timestamp, name, success, resultCode, duration, url
| order by timestamp desc
```

#### View Custom Logs
```kusto
traces
| where timestamp > ago(1h)
| where message contains "==="
| order by timestamp desc
```

## What You'll See in Logs

With the enhanced logging, you'll see:

### Frontend Logs (Browser Console)
- 🎂 Birthday App [INFO] Environment detection
- 🎂 Birthday App [DEBUG] API endpoint attempts
- 🎂 Birthday App [ERROR] Detailed error information

### Backend Logs (Application Insights)
- Request method and headers
- DOB parameter validation
- Date parsing results
- Calculation steps
- Response data
- Error stack traces

## Troubleshooting Common Issues

### Issue: No logs appearing
**Solution**: Check if Application Insights is properly connected to your Function App

### Issue: CORS errors
**Solution**: Look for "Access-Control-Allow-Origin" in the logs

### Issue: API not found
**Solution**: Check if the Function App is running and the route is correct

## Real-time Monitoring

Once set up, you can monitor your app in real-time:
1. Open Application Insights in Azure Portal
2. Go to **Live Metrics**
3. Test your app and see requests/errors in real-time