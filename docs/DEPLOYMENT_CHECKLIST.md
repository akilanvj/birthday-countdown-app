# 🚀 Azure Deployment Checklist

Use this checklist to ensure a successful deployment of your Birthday Countdown application.

## ✅ Pre-Deployment Checklist

### 📋 Prerequisites
- [ ] Azure account with active subscription
- [ ] Azure CLI installed and logged in (`az login`)
- [ ] Azure Functions Core Tools v4 installed
- [ ] GitHub account and repository created
- [ ] Code pushed to GitHub repository

### 🧪 Testing
- [ ] Run pre-deployment tests: `python3 scripts/test_before_deploy.py`
- [ ] Local server works: `python3 run_local.py`
- [ ] API responds correctly: `curl "http://localhost:8000/api/nextbirthday?dob=1990-05-15"`
- [ ] Frontend loads and functions properly
- [ ] All unit tests pass: `python -m pytest tests/ -v`

### 📁 File Structure Validation
- [ ] `src/api/function_app.py` exists and contains Azure Functions code
- [ ] `src/api/host.json` exists with version 2.0
- [ ] `src/api/requirements.txt` contains azure-functions dependency
- [ ] `src/web/index.html` exists
- [ ] `src/web/app.js` exists with correct API configuration
- [ ] `src/web/staticwebapp.config.json` exists

## 🎯 Deployment Steps

### Step 1: Deploy Azure Functions (Backend)
- [ ] Run deployment script: `./deploy/azure-deploy.sh`
- [ ] OR manually create Function App via Azure CLI
- [ ] Verify Function App is created in Azure Portal
- [ ] Test Function App URL: `https://your-function-app.azurewebsites.net/api/nextbirthday?dob=1990-05-15`
- [ ] Function returns valid JSON response

### Step 2: Deploy Static Web App (Frontend)
- [ ] Go to Azure Portal → Create Resource → Static Web Apps
- [ ] Configure with GitHub repository
- [ ] Set app location: `src/web`
- [ ] Leave API location empty (using separate Functions)
- [ ] Set output location: `.`
- [ ] Wait for deployment to complete
- [ ] Verify GitHub Actions workflow was created

### Step 3: Test Integration
- [ ] Open Static Web App URL in browser
- [ ] Enter date of birth in form
- [ ] Click "Calculate Next Birthday"
- [ ] Verify results are displayed correctly
- [ ] Test with different dates (including leap years)
- [ ] Test error cases (invalid dates, future dates)

## 🔧 Post-Deployment Configuration

### CORS Configuration (if needed)
- [ ] Configure CORS on Function App if using separate domains
- [ ] Test cross-origin requests work properly

### Custom Domain (optional)
- [ ] Add custom domain to Static Web App
- [ ] Verify SSL certificate is automatically provisioned
- [ ] Update DNS records if needed

### Monitoring Setup
- [ ] Enable Application Insights for Function App
- [ ] Set up alerts for errors or performance issues
- [ ] Configure log retention policies

## 🧪 Post-Deployment Testing

### Functional Testing
- [ ] Test all API endpoints work correctly
- [ ] Verify frontend loads on different devices/browsers
- [ ] Test form validation (client-side and server-side)
- [ ] Test error handling and user feedback
- [ ] Verify responsive design on mobile devices

### Performance Testing
- [ ] Test API response times (should be < 2 seconds)
- [ ] Verify frontend loads quickly (< 3 seconds)
- [ ] Test with multiple concurrent users
- [ ] Monitor Function App cold start times

### Security Testing
- [ ] Verify HTTPS is enforced on both frontend and API
- [ ] Test input validation prevents malicious inputs
- [ ] Verify no sensitive information is exposed in responses
- [ ] Check CORS configuration is not overly permissive

## 📊 Monitoring and Maintenance

### Regular Checks
- [ ] Monitor Function App execution logs
- [ ] Check Static Web App deployment status
- [ ] Review GitHub Actions workflow runs
- [ ] Monitor application performance metrics

### Updates and Maintenance
- [ ] Set up automated dependency updates
- [ ] Plan regular security updates
- [ ] Monitor Azure service health
- [ ] Keep documentation updated

## 🚨 Troubleshooting Common Issues

### Function App Issues
- [ ] Check Python version is 3.9
- [ ] Verify requirements.txt is correct
- [ ] Check Application Insights logs for errors
- [ ] Ensure Function App is running (not stopped)

### Static Web App Issues
- [ ] Check GitHub Actions workflow logs
- [ ] Verify build configuration is correct
- [ ] Check staticwebapp.config.json syntax
- [ ] Ensure repository permissions are correct

### Integration Issues
- [ ] Verify API URL configuration in frontend
- [ ] Check CORS settings if cross-origin requests fail
- [ ] Test API endpoints directly with curl/Postman
- [ ] Verify network connectivity between services

## 🎉 Deployment Success Criteria

Your deployment is successful when:
- [ ] ✅ Function App responds to API requests correctly
- [ ] ✅ Static Web App loads and displays properly
- [ ] ✅ Frontend can successfully call backend API
- [ ] ✅ All form validations work correctly
- [ ] ✅ Error handling provides user-friendly messages
- [ ] ✅ Application works on mobile and desktop
- [ ] ✅ HTTPS is enforced on all endpoints
- [ ] ✅ Performance meets acceptable standards

## 📞 Support Resources

If you encounter issues:
- **Azure Functions**: [Documentation](https://docs.microsoft.com/en-us/azure/azure-functions/)
- **Static Web Apps**: [Documentation](https://docs.microsoft.com/en-us/azure/static-web-apps/)
- **GitHub Actions**: [Documentation](https://docs.github.com/en/actions)
- **Azure Support**: [Create Support Ticket](https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade)

---

**🎂 Happy Deploying! Your Birthday Countdown app will be live soon! 🎉**