# 🎂 Birthday Countdown Application

A serverless web application that calculates when someone's next birthday will occur, built with Azure Functions (Python v2) and a responsive frontend.

## 🚀 Quick Start

### Local Development
```bash
# Start the local development server
python3 run_local.py

# Access the application
open http://localhost:8000
```

### Alternative Startup Methods
```bash
# Using shell script (macOS/Linux)
./scripts/start_local.sh

# Using batch file (Windows)
scripts/start_local.bat

# Direct server execution
python3 scripts/local_server.py
```

## 📁 Project Structure

```
birthday-countdown/
├── 📁 src/                    # Source code
│   ├── 📁 api/               # Azure Functions backend
│   └── 📁 web/               # Frontend web application
├── 📁 scripts/               # Development scripts
├── 📁 tests/                 # Test suites
├── 📁 docs/                  # Documentation
├── 📁 config/                # Configuration files
├── 📁 deploy/                # Deployment configurations
└── run_local.py              # Main entry point
```

## 🎯 Features

- 🎂 **Birthday Calculation**: Accurate next birthday date calculation
- 📅 **Leap Year Support**: Handles February 29 birthdays correctly
- 🎈 **Age Calculation**: Current age in complete years
- 📱 **Responsive Design**: Works on mobile, tablet, and desktop
- 🔒 **Input Validation**: Comprehensive validation and error handling
- ⚡ **Serverless Ready**: Built for Azure Functions deployment
- 🧪 **Well Tested**: Comprehensive test coverage

## 🔧 Technology Stack

- **Backend**: Python 3.9+ with Azure Functions v2 programming model
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+)
- **Development**: Local HTTP server for testing
- **Deployment**: Azure Functions + Azure Static Web Apps
- **Testing**: Python unittest framework

## 📖 Documentation

- **[Codebase Overview](docs/CODEBASE_OVERVIEW.md)** - Comprehensive technical documentation
- **[Local Development Guide](docs/LOCAL_DEVELOPMENT.md)** - Local setup and testing
- **[Requirements](/.kiro/specs/next-birthday-countdown/requirements.md)** - Detailed requirements
- **[Design Document](/.kiro/specs/next-birthday-countdown/design.md)** - Architecture and design

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test suites
python -m pytest tests/test_birthday_calculator.py
python -m pytest tests/test_integration.py

# Run with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

## 🚀 Deployment

### Quick Deploy to Azure
```bash
# Automated deployment script
./deploy/azure-deploy.sh

# Or PowerShell (Windows)
./deploy/azure-deploy.ps1
```

### Manual Deployment Steps
1. **Deploy Azure Functions (Backend)**:
   ```bash
   cd src/api
   func azure functionapp publish <your-function-app-name>
   ```

2. **Deploy Static Web App (Frontend)**:
   - Go to Azure Portal → Create Static Web App
   - Connect to GitHub repository
   - Set app location: `src/web`
   - Leave API location empty
   - Set output location: `.`

### Detailed Deployment Guide
- **[Complete Azure Deployment Guide](docs/AZURE_DEPLOYMENT.md)** - Step-by-step instructions
- **[Deployment Checklist](docs/DEPLOYMENT_CHECKLIST.md)** - Pre and post-deployment checklist

## 🔌 API Usage

**Endpoint**: `GET /api/nextbirthday?dob=YYYY-MM-DD`

**Example**:
```bash
curl "http://localhost:8000/api/nextbirthday?dob=1990-05-15"
```

**Response**:
```json
{
  "inputDob": "1990-05-15",
  "ageYears": 35,
  "nextBirthdayDate": "2026-05-15",
  "nextBirthdayDayOfWeek": "Friday",
  "daysUntilNextBirthday": 102,
  "message": "📅 Your birthday is in 102 days. Plenty of time to prepare!"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python -m pytest tests/`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using Azure Functions and modern web technologies**